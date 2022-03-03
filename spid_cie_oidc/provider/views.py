import hashlib
import logging
import urllib.parse
import uuid

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.http import (
    HttpResponseForbidden,
    HttpResponseRedirect
)
from django.forms.utils import ErrorList
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views import View
from pydantic import ValidationError
from spid_cie_oidc.entity.exceptions import InvalidEntityConfiguration
from spid_cie_oidc.entity.jwtse import (
    unpad_jwt_head,
    unpad_jwt_payload,
    verify_jws
)
from spid_cie_oidc.entity.exceptions import InvalidEntityConfiguration
from spid_cie_oidc.entity.models import FederationEntityConfiguration, TrustChain
from spid_cie_oidc.entity.settings import HTTPC_PARAMS
from spid_cie_oidc.entity.tests.settings import *
from spid_cie_oidc.entity.trust_chain_operations import get_or_create_trust_chain

from spid_cie_oidc.provider.models import IssuedToken, OidcSession

from .exceptions import AuthzRequestReplay
from .forms import *
from .settings import *

logger = logging.getLogger(__name__)


class OpBase:
    """
        Baseclass with common methods for OPs
    """

    def redirect_response_data(
        self, **kwargs
    ) -> HttpResponseRedirect:
        url = f'{self.payload["redirect_uri"]}?{urllib.parse.urlencode(kwargs)}'
        return HttpResponseRedirect(url)

    def find_jwk(self, header:dict, jwks:list) -> dict:
        for jwk in jwks:
            if header['kid'] == jwk['kid']:
                return jwk

    def validate_authz_request_object(self, req):
        try:
            self.payload = unpad_jwt_payload(req)
            header = unpad_jwt_head(req)
        except Exception as e:
            logger.error(
                f"Error in Authz request object {dict(req.GET)}: {e}"
            )
            # FIXME: if not payload it's no possible to do redirect
            return self.redirect_response_data(
                error = "invalid_request",
                error_description =_("Error in Authz request object"),
                state = self.payload["state"])

        self.is_a_replay_authz()

        rp_trust_chain = TrustChain.objects.filter(
            type = "openid_relying_party",
            sub = self.payload['iss'],
            trust_anchor__sub = settings.OIDCFED_TRUST_ANCHOR
        ).first()
        if rp_trust_chain and not rp_trust_chain.is_active:
            logger.warning(
                f"Disabled client {rp_trust_chain.sub} requests an authorization."
            )
            return self.redirect_response_data(
                # TODO: check error
                error = "access_denied",
                error_description =_(
                    f"Disabled client {rp_trust_chain.sub} requests an authorization."
                ),
                state = self.payload["state"])

        elif not rp_trust_chain or not rp_trust_chain.is_valid:
            rp_trust_chain = get_or_create_trust_chain(
                subject = self.payload['iss'],
                trust_anchor = settings.OIDCFED_TRUST_ANCHOR,
                metadata_type = 'openid_relying_party',
                httpc_params = HTTPC_PARAMS,
                required_trust_marks = getattr(
                    settings, 'OIDCFED_REQUIRED_TRUST_MARKS', []
                )
            )
            if not rp_trust_chain.is_valid:
                # FIXME: to do test
                logger.warning(
                    f"Failed trust chain validation for {self.payload['iss']}"
                )
                return self.redirect_response_data(
                    # TODO: check error
                    error = "unauthorized_client",
                    error_description =_(
                        f"Failed trust chain validation for {self.payload['iss']}."
                    ),
                    state = self.payload["state"])

        jwks = rp_trust_chain.metadata['jwks']['keys']
        jwk = self.find_jwk(header, jwks)
        if not jwk:
            logger.error(
                f"Invalid jwk for {self.payload['iss']}. "
                f"{header['kid']} not found in {jwks}"
            )
            return self.redirect_response_data(
                # TODO: check error
                error = "unauthorized_client",
                error_description =_(f"Invalid jwk for {self.payload['iss']}."),
                state = self.payload["state"])

        try:
            verify_jws(req, jwk)
        except Exception as e:
            # FIXME: to do test
            logger.error(
                "Authz request object signature validation failed "
                f"for {self.payload['iss']}: {e} "
            )
            return self.redirect_response_data(
                # TODO: check error
                error = "access_denied",
                error_description =_(
                    "Authz request object signature validation failed "
                    f"for {self.payload['iss']}: {e} "
                ),
                state = self.payload["state"])

        return rp_trust_chain

    def is_a_replay_authz(self):
        preexistent_authz = OidcSession.objects.filter(
            client_id = self.payload["client_id"],
            nonce = self.payload['nonce']
        )
        if preexistent_authz:
            raise AuthzRequestReplay(
                f"{preexistent_authz.client_id} with {preexistent_authz.nonce}"
            )


class AuthzRequestView(OpBase, View):
    """View which processes the actual Authz request and
    returns a Http Redirect
    """
    template = "op_user_login.html"

    def validate_authz(self, payload: dict):

        must_list = ('scope', 'acr_values')
        for i in must_list:
            if isinstance(payload.get(i, None), str):
                payload[i] = [payload[i]]

        redirect_uri = payload.get('redirect_uri', "")
        p = urllib.parse.urlparse(redirect_uri)
        scheme_fqdn = f"{p.scheme}://{p.hostname}"
        if payload['client_id'] in scheme_fqdn:
            raise ValidationError(
                f"{payload.get('client_id', None)} not in {redirect_uri}"
            )

        schema = OIDCFED_PROVIDER_PROFILES[OIDCFED_DEFAULT_PROVIDER_PROFILE]
        schema["authorization_request"](**payload)

    def get_login_form(self):
        return AuthLoginForm

    def get(self, request, *args, **kwargs):
        """
            authz request object is received here
            it's validated and a login prompt is rendered to the user
        """
        req = request.GET.get('request', None)
        # FIXME: invalid check: if not request-> no payload-> no redirect_uri
        if not req:
            logger.error(
                f"Missing Authz request object in {dict(request.GET)}"
            )
            return self.redirect_response_data(
                error = "invalid_request",
                error_description =_("Missing Authz request object"),
                # No req -> no payload -> no state
                state = "")
        # yes, again. We MUST.
        tc = None
        try:
            tc = self.validate_authz_request_object(req)
            if type(tc) == HttpResponseRedirect:
                return tc
        except InvalidEntityConfiguration as e:
            # FIXME: to do test
            logger.error(f" {e}")
            return self.redirect_response_data(
                error = "invalid_request",
                error_description =_("Failed to establish the Trust"),
            )
        except AuthzRequestReplay as e:
            logger.error(
                "Replay on authz request detected for "
                f"{request.GET.get('client_id', 'unknow')}: {e}"
            )
            return self.redirect_response_data(
                error = "invalid_request",
                error_description =_(
                    "An Unknown error raised during validation of "
                    f" authz request object: {e}"
                )
            )

        except Exception as e:
            # FIXME: to do test
            logger.error(
                "Error during trust build for "
                f"{request.GET.get('client_id', 'unknow')}: {e}"
            )
            return self.redirect_response_data(
                error = "invalid_request",
                error_description =_(
                    "An Unknown error raised during validation of "
                    f" authz request object: {e}"
                )
            )

        try:
            self.validate_authz(self.payload)
        except ValidationError as e:
            logger.error(
                "Authz request object validation failed "
                f"for {self.payload['iss']}: {e} "
            )
            return self.redirect_response_data(
                # TODO: check error
                error = "invalid_request",
                error_description =_(
                    "Authz request object validation failed "
                    f"for {self.payload['iss']}: {e} "),
                state = self.payload["state"])

        # stores the authz request in a hidden field in the form
        form = self.get_login_form()(dict(authz_request_object=req))
        context = {
            "client_organization_name": tc.metadata.get(
                "client_name", self.payload['client_id']
            ),
            "client_redirect_uri": self.payload.get(
                "redirect_uri", "#"
            ),
            "form": form
        }
        return render(request, self.template, context)

    def post(self, request, *args, **kwargs):
        """
            When the User prompts his credentials
        """
        form = self.get_login_form()(request.POST)
        if not form.is_valid():
            return render(request, self.template, {'form': form})

        error = False
        authz_request = form.cleaned_data.get('authz_request_object')

        try:
            self.validate_authz_request_object(authz_request)
        except Exception as e:
            error = True
        # non si può mettere dentro except?
        if error:
            logger.error(
                "Authz request object validation failed "
                f"for {authz_request}: {e} "
            )
            return self.redirect_response_data(
                # TODO: check error
                error = "invalid_request",
                error_description =_(
                    "Authz request object validation failed "
                    f"for {authz_request}: {e}")
            )

        # autenticate the user
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(username=username, password=password)
        if not user:
            errors = form._errors.setdefault("username", ErrorList())
            errors.append(_("invalid username or password"))
            return render(request, self.template, {'form': form})
        else:
            login(request, user)

        # create auth_code
        auth_code = hashlib.sha512(
            f'{uuid.uuid4()}-{self.payload["client_id"]}-{self.payload["nonce"]}'.encode()
        ).hexdigest()

        # put the auth_code in the user web session
        request.session['oidc'] = {'auth_code': auth_code}

        # store the User session
        OidcSession.objects.create(
            user = user,
            user_uid = user.username,
            nonce = self.payload['nonce'],
            authz_request = self.payload,
            sub = self.payload["sub"],
            client_id = self.payload["client_id"],
            auth_code = auth_code
        )
        consent_url = reverse('oidc_provider_consent')
        return HttpResponseRedirect(consent_url)


class ConsentPageView(OpBase, View):
    # create a redirect with auth code, scope, state and iss in it ???? lo scope nelle linee guida non c'è

    template = "op_user_consent.html"

    def get_consent_form(self):
        return ConsentPageForm

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            # FIXME: to do test
            return HttpResponseForbidden()

        auth_code = request.session.get('oidc', {}).get("auth_code", None)
        if not auth_code:
            # FIXME: to do test
            return HttpResponseForbidden()

        session = OidcSession.objects.filter(
            user = request.user,
            auth_code = auth_code,
            revoked = False
        ).first()

        if not session:
            return HttpResponseForbidden()
        
        tc = TrustChain.objects.filter(
            sub=session.client_id,
            type = "openid_relying_party"
        ).first()

        # if this auth code has already been used ... forbidden
        if IssuedToken.objects.filter(session=session):
            logger.warning(f"Auth code Replay {session}")
            return HttpResponseForbidden()

        # get up fresh claims
        user_claims = request.user.attributes
        user_claims['email'] = user_claims.get('email', request.user.email)
        user_claims['username'] = request.user.username

        # TODO: mapping with human names
        # filter on requested claims
        filtered_user_claims = []
        for target, claims in session.authz_request.get('claims', {}).items():
            for claim in claims:
                if claim in user_claims:
                    filtered_user_claims.append(claim)
        #

        # TODO: create a form with the consent submission
        # stores the authz request in a hidden field in the form
        context = {
            "form": self.get_consent_form()(),
            "session": session,
            "client_organization_name": tc.metadata.get(
                'client_name', session.client_id
            ),
            "user_claims": set(filtered_user_claims)
        }
        return render(request, self.template, context)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            # FIXME: to do test
            return HttpResponseForbidden()

        session = OidcSession.objects.filter(
            auth_code = request.session['oidc']['auth_code'],
            user = request.user
        ).first()

        if not session:
            return HttpResponseForbidden()

        self.payload = session.authz_request
        # TODO: create a form with the consent submission
        form = self.get_consent_form()(request.POST)
        if not form.is_valid():
            return self.redirect_response_data(
                # TODO: this is not normative -> check AgID/IPZS
                error = "rejected_by_user",
                error_description =_(
                    "User rejected the release of attributes"
                )
            )

        issuer = FederationEntityConfiguration.objects.filter(
                entity_type = 'openid_provider'
        ).first()

        return self.redirect_response_data(
            code = session.auth_code,
            state = session.authz_request['state'],
            iss = issuer.sub if issuer else ""
        )


class TokenEndpoint(View):

    def get(self, request, *args, **kwargs):
        pass

    def post(self, request, *args, **kwargs):
        pass


class UserInfoEndpoint(View):

    def get(self, request, *args, **kwargs):
        pass

    def post(self, request, *args, **kwargs):
        pass


class IntrospectionEndpoint(View):

    def get(self, request, *args, **kwargs):
        pass

    def post(self, request, *args, **kwargs):
        pass
