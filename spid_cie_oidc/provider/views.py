import logging
import urllib.parse
import uuid

from django.conf import settings
from django.contrib.auth import authenticate
from django.http import (
    HttpResponseForbidden,
    HttpResponseRedirect
)
from django.shortcuts import render
from django.utils.translation import gettext as _
from django.views import View
from pydantic import ValidationError
from spid_cie_oidc.entity.jwtse import (
    unpad_jwt_head,
    unpad_jwt_payload,
    verify_jws
)
from spid_cie_oidc.entity.exceptions import InvalidEntityConfiguration
from spid_cie_oidc.entity.models import TrustChain
from spid_cie_oidc.entity.settings import HTTPC_PARAMS
from spid_cie_oidc.entity.tests.settings import *
from spid_cie_oidc.entity.trust_chain_operations import \
    get_or_create_trust_chain

from spid_cie_oidc.provider.models import OidcSession

from .forms import *
from . settings import *

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
            return self.redirect_response_data(
                error = "invalid_request",
                error_description =_("Error in Authz request object"),
                state = self.payload["state"])

        rp_trust_chain = TrustChain.objects.filter(
            type = "openid_relying_party",
            sub = self.payload['iss']
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
                trust_anchor = settings.OIDCFED_FEDERATION_TRUST_ANCHOR,
                metadata_type = 'openid_relying_party',
                httpc_params = HTTPC_PARAMS,
                required_trust_marks = getattr(
                    settings, 'OIDCFED_REQUIRED_TRUST_MARKS', []
                )
            )
            if not rp_trust_chain.is_valid:
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

        return self.payload


class AuthzRequestView(OpBase, View):
    """View which processes the actual Authz request and
    returns a Http Redirect
    """
    template = "user_login.html"

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
        try:
            self.validate_authz_request_object(req)
        except InvalidEntityConfiguration as e:
            logger.error(f" {e}")
            return self.redirect_response_data(
                error = "invalid_request",
                error_description =_("Failed to establish the Trust"),
            )
        except Exception as e:
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

        authz_request = form.cleaned_data['authz_request_object']
        self.validate_authz_request_object()

        # autenticate the user
        form_dict = {**form.cleaned_data}
        username = form_dict.get("username")
        password = form_dict.get("password")
        user = authenticate(username=username, password=password)
        userinfo_claims = self.payload["claims"]["userinfo"]
        # creare auth_code
        auth_code = uuid.uuid4()
        # store the User session
        OidcSession.objects.create(
            user = user, authz_request = authz_request, sub = self.payload["sub"],
            client_id = self.payload["client_id"], userinfo_claims = userinfo_claims,
            user_uid = user.uid, auth_code = auth_code)

        # show to the user the a consent page
        consent_url = reverse('oidc_provider_consent')
        breakpoint()
        return HttpResponseRedirect(consent_url)


class ConsentPageView(OpBase, View):
    # create a redirect with auth code, scope, state and iss in it ???? lo scope nelle linee guida non c'è

    template = "op_user_consent.html"

    def get_consent_form(self):
        return ConsentPageForm

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise HttpResponseForbidden()

        # TODO: create a form with the consent submission
        # stores the authz request in a hidden field in the form
        context = {
            "form": self.get_consent_form()()
        }
        return render(request, self.template, context)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            # TODO: what are the audience? RP or End User
            raise HttpResponseForbidden()

        # TODO: create a form with the consent submission
        # stores the authz request in a hidden field in the form ?????NON SERVE é tutto nella sessione
        form = self.get_consent_form()(request.POST)
        if not form.is_valid():
            # user doesn't give his consent, redirect to an error page
            # TODO: remember to logout the user first!
            # TODO: what are the audience? RP or End User
            raise HttpResponseForbidden()
        session = OidcSession.objects.filter()
        if not session:
            # TODO: what are the audience? RP or End User
            raise HttpResponseForbidden()

        # iss, state e code li recupero dalla session
        return self.redirect_response_data(
            code = "",
            state = "",
            iss = ""
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
