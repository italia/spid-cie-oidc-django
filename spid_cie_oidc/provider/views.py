import base64
import hashlib
import logging
import urllib.parse
import uuid

from cryptojwt.jws.utils import left_hash
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.forms.utils import ErrorList
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    HttpResponseRedirect,
    JsonResponse
)
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from pydantic import ValidationError
from spid_cie_oidc.entity.exceptions import InvalidEntityConfiguration
from spid_cie_oidc.entity.jwtse import (
    create_jws,
    encrypt_dict,
    unpad_jwt_head,
    unpad_jwt_payload,
    verify_jws
)
from spid_cie_oidc.entity.models import (
    FederationEntityConfiguration,
    TrustChain
)
from spid_cie_oidc.entity.settings import HTTPC_PARAMS
from spid_cie_oidc.entity.tests.settings import *
from spid_cie_oidc.entity.trust_chain_operations import get_or_create_trust_chain
from spid_cie_oidc.entity.utils import (
    datetime_from_timestamp,
    exp_from_now,
    iat_now
)
from spid_cie_oidc.provider.models import IssuedToken, OidcSession

from .exceptions import AuthzRequestReplay, InvalidSession, RevokedSession
from .forms import *
from .settings import *

logger = logging.getLogger(__name__)


class OpBase:
    """
    Baseclass with common methods for OPs
    """

    def redirect_response_data(self, **kwargs) -> HttpResponseRedirect:
        url = f'{self.payload["redirect_uri"]}?{urllib.parse.urlencode(kwargs)}'
        return HttpResponseRedirect(url)

    def find_jwk(self, header: dict, jwks: list) -> dict:
        for jwk in jwks:
            if header["kid"] == jwk["kid"]:
                return jwk

    def validate_authz_request_object(self, req) -> TrustChain:
        try:
            self.payload = unpad_jwt_payload(req)
            header = unpad_jwt_head(req)
        except Exception as e:
            # FIXME: if not payload it's no possible to do redirect
            state = self.payload["state"]
            logger.error(
                f"Error in Authz request object {dict(req.GET)}: {e}."
                f" error=invalid_request"
                f"state={state}"
            )
            raise Exception()

        self.is_a_replay_authz()
        rp_trust_chain = TrustChain.objects.filter(
            type="openid_relying_party",
            sub=self.payload["iss"],
            trust_anchor__sub=settings.OIDCFED_DEFAULT_TRUST_ANCHOR
        ).first()
        if rp_trust_chain and not rp_trust_chain.is_active:
            state = self.payload["state"]
            logger.warning(
                f"Disabled client {rp_trust_chain.sub} requests an authorization. "
                "error = access_denied, "
                f"state={state}"
            )
            raise Exception()

        elif not rp_trust_chain or rp_trust_chain.is_expired:
            rp_trust_chain = get_or_create_trust_chain(
                subject=self.payload["iss"],
                trust_anchor=settings.OIDCFED_DEFAULT_TRUST_ANCHOR,
                metadata_type="openid_relying_party",
                httpc_params=HTTPC_PARAMS,
                required_trust_marks=getattr(
                    settings, "OIDCFED_REQUIRED_TRUST_MARKS", []
                ),
            )
            if not rp_trust_chain.is_valid:
                # FIXME: to do test
                state = self.payload["iss"]
                logger.warning(
                    f"Failed trust chain validation for {self.payload['iss']}. "
                    "error=unauthorized_client, "
                    f"state={state}"
                )
                raise Exception()

        jwks = rp_trust_chain.metadata["jwks"]["keys"]
        jwk = self.find_jwk(header, jwks)
        if not jwk:
            state = self.payload["iss"]
            logger.error(
                f"Invalid jwk for {self.payload['iss']}. "
                f"{header['kid']} not found in {jwks}. "
                "error=unauthorized_client, "
                f"state={state}"
            )
            raise Exception()

        try:
            verify_jws(req, jwk)
        except Exception as e:
            # FIXME: to do test
            state = self.payload["iss"]
            logger.error(
                "Authz request object signature validation failed "
                f"for {self.payload['iss']}: {e}. "
                "error=access_denied, "
                f"state={state}"
            )
            raise Exception()

        return rp_trust_chain

    def is_a_replay_authz(self):
        preexistent_authz = OidcSession.objects.filter(
            client_id=self.payload["client_id"],
            nonce=self.payload["nonce"]
        ).first()
        if preexistent_authz:
            raise AuthzRequestReplay(
                f"{preexistent_authz.client_id} with {preexistent_authz.nonce}"
            )

    def check_session(self, request) -> OidcSession:
        if not request.user.is_authenticated:
            raise InvalidSession()

        auth_code = request.session.get("oidc", {}).get("auth_code", None)
        if not auth_code:
            # FIXME: to do test
            raise InvalidSession()

        session = OidcSession.objects.filter(
            auth_code=request.session["oidc"]["auth_code"],
            user=request.user
        ).first()

        if not session:
            raise InvalidSession()

        if session.revoked:
            raise RevokedSession()

        return session

    def get_issuer(self):
        return FederationEntityConfiguration.objects.filter(
            entity_type="openid_provider"
        ).first()

    def check_client_assertion(self, client_id: str, client_assertion: str) -> bool:
        head = unpad_jwt_head(client_assertion)
        payload = unpad_jwt_payload(client_assertion)
        if payload['sub'] != client_id:
            # TODO Specialize exceptions
            raise Exception()

        tc = TrustChain.objects.get(sub=client_id, is_active=True)
        jwk = self.find_jwk(head, tc.metadata['jwks']['keys'])
        verify_jws(client_assertion, jwk)

        return True


class AuthzRequestView(OpBase, View):
    """
        View which processes the actual Authz request and
        returns a Http Redirect
    """

    template = "op_user_login.html"

    def validate_authz(self, payload: dict):

        must_list = ("scope", "acr_values")
        for i in must_list:
            if isinstance(payload.get(i, None), str):
                payload[i] = [payload[i]]

        redirect_uri = payload.get("redirect_uri", "")
        p = urllib.parse.urlparse(redirect_uri)
        scheme_fqdn = f"{p.scheme}://{p.hostname}"
        if payload["client_id"] in scheme_fqdn:
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
        req = request.GET.get("request", None)
        # FIXME: invalid check: if not request-> no payload-> no redirect_uri
        if not req:
            logger.error(
                f"Missing Authz request object in {dict(request.GET)}"
                f"error=invalid_request"
            )
            return self.redirect_response_data(
                error="invalid_request",
                error_description=_("Missing Authz request object"),
                # No req -> no payload -> no state
                state="",
            )
        # yes, again. We MUST.
        tc = None

        try:
            tc = self.validate_authz_request_object(req)
        except InvalidEntityConfiguration as e:
            # FIXME: to do test
            logger.error(f" {e}")
            return self.redirect_response_data(
                error="invalid_request",
                error_description=_("Failed to establish the Trust"),
            )
        except AuthzRequestReplay as e:
            logger.error(
                "Replay on authz request detected for "
                f"{request.GET.get('client_id', 'unknow')}: {e}"
            )
            return self.redirect_response_data(
                error="invalid_request",
                error_description=_(
                    "An Unknown error raised during validation of "
                    f" authz request object: {e}"
                ),
            )

        except Exception as e:
            logger.error(
                "Error during trust build for "
                f"{request.GET.get('client_id', 'unknown')}: {e}"
            )
            return self.redirect_response_data(
                error="invalid_request",
                error_description=_("Authorization request not valid"),
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
                error="invalid_request",
                error_description=_(
                    "Authz request object validation failed "
                    f"for {self.payload['iss']}: {e} "
                ),
                state=self.payload["state"],
            )

        # stores the authz request in a hidden field in the form
        form = self.get_login_form()(dict(authz_request_object=req))
        context = {
            "client_organization_name": tc.metadata.get(
                "client_name", self.payload["client_id"]
            ),
            "client_redirect_uri": self.payload.get("redirect_uri", "#"),
            "form": form,
        }
        return render(request, self.template, context)

    def post(self, request, *args, **kwargs):
        """
        When the User prompts his credentials
        """
        form = self.get_login_form()(request.POST)
        if not form.is_valid():
            return render(request, self.template, {"form": form})

        authz_request = form.cleaned_data.get("authz_request_object")

        try:
            self.validate_authz_request_object(authz_request)
        except Exception as e:
            logger.error(
                "Authz request object validation failed " f"for {authz_request}: {e} "
            )
            return self.redirect_response_data(
                # TODO: check error
                error="invalid_request",
                error_description=_(
                    "Authz request object validation failed "
                    f"for {authz_request}: {e}"
                ),
            )

        # autenticate the user
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(username=username, password=password)
        if not user:
            errors = form._errors.setdefault("username", ErrorList())
            errors.append(_("invalid username or password"))
            return render(request, self.template, {"form": form})
        else:
            login(request, user)

        # create auth_code
        auth_code = hashlib.sha512(
            '-'.join(
                (
                    f'{uuid.uuid4()}',
                    f'{self.payload["client_id"]}',
                    f'{self.payload["nonce"]}'
                )
            ).encode()
        ).hexdigest()

        # put the auth_code in the user web session
        request.session["oidc"] = {"auth_code": auth_code}

        # store the User session
        session = OidcSession.objects.create(
            user=user,
            user_uid=user.username,
            nonce=self.payload["nonce"],
            authz_request=self.payload,
            client_id=self.payload["client_id"],
            auth_code=auth_code,
        )
        session.set_sid(request)

        consent_url = reverse("oidc_provider_consent")
        return HttpResponseRedirect(consent_url)


class ConsentPageView(OpBase, View):

    template = "op_user_consent.html"

    def get_consent_form(self):
        return ConsentPageForm

    def get(self, request, *args, **kwargs):
        try:
            session = self.check_session(request)
        except Exception:
            logger.warning("Invalid session")
            return HttpResponseForbidden()

        tc = TrustChain.objects.filter(
            sub=session.client_id, type="openid_relying_party"
        ).first()

        # if this auth code has already been used ... forbidden
        if IssuedToken.objects.filter(session=session):
            logger.warning(f"Auth code Replay {session}")
            return HttpResponseForbidden()

        # get up fresh claims
        user_claims = request.user.attributes
        user_claims["email"] = user_claims.get("email", request.user.email)
        user_claims["username"] = request.user.username

        # TODO: mapping with human names
        # filter on requested claims
        filtered_user_claims = []
        for target, claims in session.authz_request.get("claims", {}).items():
            for claim in claims:
                if claim in user_claims:
                    filtered_user_claims.append(claim)
        #

        context = {
            "form": self.get_consent_form()(),
            "session": session,
            "client_organization_name": tc.metadata.get(
                "client_name", session.client_id
            ),
            "user_claims": set(filtered_user_claims),
        }
        return render(request, self.template, context)

    def post(self, request, *args, **kwargs):
        try:
            session = self.check_session(request)
        except Exception:
            logger.warning("Invalid session")
            return HttpResponseForbidden()

        self.payload = session.authz_request
        form = self.get_consent_form()(request.POST)
        if not form.is_valid():
            return self.redirect_response_data(
                # TODO: this is not normative -> check AgID/IPZS
                error="rejected_by_user",
                error_description=_("User rejected the release of attributes"),
            )

        issuer = self.get_issuer()

        return self.redirect_response_data(
            code=session.auth_code,
            state=session.authz_request["state"],
            iss=issuer.sub if issuer else "",
        )


@method_decorator(csrf_exempt, name="dispatch")
class TokenEndpoint(OpBase, View):
    def get_jwt_common_data(self):
        return {
            "jti": str(uuid.uuid4()),
            "exp": exp_from_now(),
            "iat": iat_now()
        }

    def get(self, request, *args, **kwargs):
        return HttpResponseBadRequest()

    def grant_auth_code(self, request, *args, **kwargs):
        """
        Example of a Token request:

        {
            'grant_type': ['authorization_code'],
            'redirect_uri': ['http://127.0.0.1:8000/oidc/rp/callback'],
            'client_id': ['http://127.0.0.1:8000/oidc/rp/'],
            'state': ['tiIjdMSE20tuIWwruFhYaDROadKxKO9x'],
            'code': [
                '7348f5dd913e96e6db480662d4717b8a3669ba04b49f690773af693ae4d7'
                '228f2fbeb6fbf418306192be27ed79c24ecb21a099308f9ec3337fd8e6433a5c5ccc'
            ],
            'code_verifier': ['WGzumG7gKBioHAWNc567YTPoLBQxRyrVqsl6TJPC8XmQ8flbPbUsHQ'],
            'client_assertion_type': ['urn:ietf:params:oauth:client-assertion-type:jwt-bearer'],
            'client_assertion': [
                'eyJhbGciOiJSUzI1NiIsImtpZCI6IjJIbm9GUzNZbkM5dGppQ2FpdmhXTFZVSjNBeHdHR3pfOTh1UkZhcU1FRXMifQ.'
                'eyJpc3MiOiJodHRwOi8vMTI3LjAuMC4xOjgwMDAvb2lkYy9ycC8iLCJzdWIiOiJodHRwOi8vMTI3LjAuMC4xOjgwMDAvb2lkYy9ycC8iLC'
                'JhdWQiOlsiaHR0cDovLzEyNy4wLjAuMTo4MDAwL29pZGMvb3AvdG9rZW4vIl0sImlhdCI6MTY0NjQzODQ2OCwiZXhwIjoxNjQ2NDQwNDQ'
                '4LCJqdGkiOiJjODRjYjZkMy0wN2VjLTQxNjktODA3OC05MDQ3NTk0MzNiYzQifQ.u2uK3zN_UvsmWsPVuNlaD8VEaJTSOUg5_3Y7mufrZF'
                '_-O-IwyZk3kfukgLWpxqIPJi531aVt4X5YSofgf3IhORmZqx7buUFP1LjlKC03-dSXTHlhhWqwtp2gyI4hjUPTQvRaNfIJ6icVRXiKuPUUJ0'
                '0inqDQISxZtvIooGm3M7-GNtDroAx4aa3BSxxytG48v4-mDKJ_K04FOGI82JHmAIca1H_eHoC_vMoAGWwQNwvMbpS26F1J0s7bqWnmTE1JF_'
                't--2FJZkVRRdOwzIxgZhEZsXIM6tUovDmHHIIh3K1QiTIwM-v_SuHpDO9sXi8IwhwAes8xiWAL2rwHyDkJgA'
            ]
        }
        """
        # PKCE check - based on authz.authz_request["code_challenge_method"] == S256
        code_challenge = hashlib.sha256(request.POST["code_verifier"].encode()).digest()
        code_challenge = base64.urlsafe_b64encode(code_challenge).decode("utf-8")
        code_challenge = code_challenge.replace("=", "")
        if code_challenge != self.authz.authz_request["code_challenge"]:
            return HttpResponseForbidden()
        #

        _sub = self.authz.pairwised_sub()
        access_token = {
            "iss": self.issuer.sub,
            "sub": _sub,
            "aud": [self.authz.client_id],
            "client_id": self.authz.client_id,
            "scope": self.authz.authz_request["scope"],
        }
        access_token.update(self.commons)
        jwt_at = create_jws(access_token, self.issuer.jwks[0], typ="at+jwt")

        id_token = {
            "sub": _sub,
            "nonce": self.authz.authz_request["nonce"],
            "at_hash": left_hash(jwt_at, "HS256"),
            "c_hash": left_hash(self.authz.auth_code, "HS256"),
            "aud": [self.authz.client_id],
            "iss": self.issuer.sub,
        }
        id_token.update(self.commons)
        jwt_id = create_jws(id_token, self.issuer.jwks[0])

        iss_token_data = dict(
            session=self.authz,
            access_token=jwt_at,
            id_token=jwt_id,
            expires=datetime_from_timestamp(self.commons["exp"])
        )

        # refresh token is scope offline_access and prompt == consent
        if (
            "offline_access" in self.authz.authz_request['scope'] and
            'consent' in self.authz.authz_request['prompt']
        ):
            refresh_token = {
                "sub": _sub,
                "at_hash": left_hash(jwt_at, "HS256"),
                "c_hash": left_hash(self.authz.auth_code, "HS256"),
                "aud": [self.authz.client_id],
                "iss": self.issuer.sub,
            }
            id_token.update(self.commons)
            iss_token_data['refresh_token'] = refresh_token

        IssuedToken.objects.create(**iss_token_data)

        expires_in = timezone.timedelta(
            seconds = access_token['exp'] - access_token['iat']
        ).seconds

        return JsonResponse(
            {
                "access_token": jwt_at,
                "id_token": jwt_id,
                "token_type": "bearer",
                "expires_in": expires_in,
                # TODO: remove unsupported scope
                "scope": self.authz.authz_request["scope"],
            }
        )

    def grant_refresh_token(self, request, *args, **kwargs):
        """
            client_id=https://rp.cie.it&
            client_assertion=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IlNQSUQiLCJhZG1pbiI6dHJ1ZX0.LVyRDPVJm0S9q7oiXcYVIIqGWY0wWQlqxvFGYswL...&
            client_assertion_type=urn%3Aietf%3Aparams%3Aoauth%3Aclient-assertion-type%3Ajwt-bearer&
            refresh_token=8xLOxBtZp8 &
            grant_type=refresh_token
        """

        # 1. get the IssuedToken refresh one, revoked = None
        # 2. create a new instance of issuedtoken linked to the same sessions and revoke the older
        # 3. response with a new refresh, access and id_token
        issuedToken = IssuedToken.objects.filter(
            refresh_token = request.POST['refresh_token'],
            revoked = False
        ).first()

        if not issuedToken:
            return JsonResponse(
                {
                    "error": "Invalid request",
                    "error_description": "Refresh token not found",

                },
                status = 400
            )

        session = issuedToken.session
        _sub = self.authz.pairwised_sub()
        refresh_token = {
            "iss": self.issuer.sub,
            "sub": _sub,
            "aud": [self.authz.client_id],
            "client_id": self.authz.client_id,
            "scope": self.authz.authz_request["scope"],
        }
        refresh_token.update(self.commons)
        jwt_rt = create_jws(refresh_token, self.issuer.jwks[0], typ="at+jwt")

        access_token = {
            "iss": self.issuer.sub,
            "sub": _sub,
            "aud": [self.authz.client_id],
            "client_id": self.authz.client_id,
            "scope": self.authz.authz_request["scope"],
        }
        access_token.update(self.commons)
        jwt_at = create_jws(access_token, self.issuer.jwks[0], typ="at+jwt")

        id_token = {
            "sub": _sub,
            "nonce": self.authz.authz_request["nonce"],
            "at_hash": left_hash(jwt_at, "HS256"),
            "c_hash": left_hash(self.authz.auth_code, "HS256"),
            "aud": [self.authz.client_id],
            "iss": self.issuer.sub,
        }
        id_token.update(self.commons)
        jwt_id = create_jws(id_token, self.issuer.jwks[0])

        iss_token_data = dict(
            session=session,
            access_token=jwt_at,
            refresh_token=jwt_rt,
            id_token = jwt_id,
            expires=datetime_from_timestamp(self.commons["exp"])
        )
        IssuedToken.objects.create(**iss_token_data)

        expires_in = timezone.timedelta(
            seconds = access_token['exp'] - access_token['iat']
        ).seconds

        issuedToken.revoked = True
        issuedToken.save()
        return JsonResponse(
            {
                "access_token": jwt_at,
                "token_type": "bearer",
                "refresh_token": jwt_at,
                "id_token": jwt_id,
                "expires_in": expires_in,
                "scope": self.authz.authz_request["scope"],
            }
        )

    def post(self, request, *args, **kwargs):
        logger.debug(f"{request.headers}: {request.POST}")
        try:
            schema = OIDCFED_PROVIDER_PROFILES[OIDCFED_DEFAULT_PROVIDER_PROFILE]
            schema[request.POST["grant_type"]](**request.POST.dict())
        except ValidationError as e:
            logger.error(
                "Token request object validation failed "
                f"for {request.POST.get('client_id', None)}: {e} "
            )
            return JsonResponse(
                {
                    "error": "invalid_request",
                    "error_description": "Token request object validation failed ",
                }
            )

        self.commons = self.get_jwt_common_data()
        self.issuer = self.get_issuer()

        self.authz = OidcSession.objects.filter(
            auth_code=request.POST["code"],
            revoked=False
        ).first()

        if not self.authz:
            return HttpResponseBadRequest()

        # check client_assertion and client ownership
        try:
            self.check_client_assertion(
                request.POST['client_id'],
                request.POST['client_assertion']
            )
        except Exception:
            # TODO: coverage test
            return JsonResponse(
                # TODO: error message here
                {
                    'error': "...",
                    'error_description': "..."

                }, status = 403
            )

        if request.POST.get("grant_type") == 'authorization_code':
            return self.grant_auth_code(request)
        elif request.POST.get("grant_type") == 'refresh_token':
            return self.grant_refresh_token(request)
        else:
            raise NotImplementedError()


class UserInfoEndpoint(OpBase, View):
    def get(self, request, *args, **kwargs):

        ah = request.headers.get("Authorization", None)
        if not ah or "Bearer " not in ah:
            return HttpResponseForbidden()
        bearer = ah.split("Bearer ")[1]

        token = IssuedToken.objects.filter(
            access_token=bearer,
            revoked=False,
            session__revoked=False,
            expires__gte=timezone.localtime(),
        ).first()

        if not token:
            return HttpResponseForbidden()

        rp_tc = TrustChain.objects.filter(
            sub=token.session.client_id,
            type="openid_relying_party",
            is_active=True
        ).first()
        if not rp_tc:
            return HttpResponseForbidden()

        issuer = self.get_issuer()
        access_token_data = unpad_jwt_payload(token.access_token)

        # TODO: user claims
        jwt = {"sub": access_token_data["sub"]}
        for claim in (
            token.session.authz_request.get("claims", {}).get("userinfo", {}).keys()
        ):
            if claim in token.session.user.attributes:
                jwt[claim] = token.session.user.attributes[claim]

        # sign the data
        jws = create_jws(jwt, issuer.jwks[0])

        # encrypt the data
        jwe = encrypt_dict(jws, rp_tc.metadata["jwks"]["keys"][0])
        return HttpResponse(jwe, content_type="application/jose")


@method_decorator(csrf_exempt, name="dispatch")
class RevocationEndpoint(OpBase,View):

    def post(self, request, *args, **kwargs):
        try:
            schema = OIDCFED_PROVIDER_PROFILES[OIDCFED_DEFAULT_PROVIDER_PROFILE]
            schema["revocation_request"](**request.POST.dict())
        except ValidationError as e:
            logger.error(
                "Revocation request object validation failed "
                f"for {request.POST.get('client_id', None)}: {e} "
            )
            return JsonResponse(
                {
                    "error": "invalid_request",
                    "error_description": "Revocation request object validation failed ",
                }
            )
        try:
            self.check_client_assertion(
                request.POST['client_id'],
                request.POST['client_assertion']
            )
        except Exception:
            return HttpResponseForbidden()

        access_token = request.POST.get('token', None)
        if not access_token:
            return HttpResponseBadRequest()

        token = IssuedToken.objects.filter(
            access_token= access_token,
            revoked = False
        ).first()

        if not token or token.expired:
            return HttpResponseForbidden()

        if access_token.is_revoked:
            return HttpResponseForbidden()

        access_token.session.revoke()
        return HttpResponse()


class IntrospectionEndpoint(View):
    def get(self, request, *args, **kwargs):
        pass

    def post(self, request, *args, **kwargs):
        pass
