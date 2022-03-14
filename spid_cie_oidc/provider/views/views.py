import base64
import hashlib
import logging
import urllib.parse
import uuid

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.forms import ValidationError
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
from pydantic import ValidationError as pydantic_ValidationError
from spid_cie_oidc.entity.exceptions import InvalidEntityConfiguration
from spid_cie_oidc.entity.jwtse import (
    create_jws,
    encrypt_dict,
    unpad_jwt_payload
)
from spid_cie_oidc.entity.models import (
    TrustChain
)
from spid_cie_oidc.entity.tests.settings import *
from spid_cie_oidc.provider.models import IssuedToken, OidcSession

from spid_cie_oidc.provider.exceptions import AuthzRequestReplay
from spid_cie_oidc.provider.forms import *
from spid_cie_oidc.provider.settings import *

from . import OpBase
logger = logging.getLogger(__name__)


class AuthzRequestView(OpBase, View):
    """
        View which processes the actual Authz request and
        returns a Http Redirect
    """

    template = "op_user_login.html"

    def validate_authz(self, payload: dict) -> None:

        must_list = ("scope", "acr_values")
        for i in must_list:
            if isinstance(payload.get(i, None), str):
                payload[i] = [payload[i]]

        redirect_uri = payload.get("redirect_uri", "")
        p = urllib.parse.urlparse(redirect_uri)
        scheme_fqdn = f"{p.scheme}://{p.hostname}"
        if payload.get("client_id", None) in scheme_fqdn:
            raise ValidationError("client_id not in redirect_uri")

        self.validate_json_schema(
            payload,
            "authorization_request",
            "Authen request object validation failed "
        )

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
                f"Missing Authz request object in {dict(request.GET)} "
                f"error=invalid_request"
            )
            return self.redirect_response_data(
                self.payload["redirect_uri"],
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
                self.payload["redirect_uri"],
                error="invalid_request",
                error_description=_("Failed to establish the Trust"),
            )
        except AuthzRequestReplay as e:
            logger.error(
                "Replay on authz request detected for "
                f"{request.GET.get('client_id', 'unknow')}: {e}"
            )
            return self.redirect_response_data(
                self.payload["redirect_uri"],
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
                self.payload["redirect_uri"],
                error="invalid_request",
                error_description=_("Authorization request not valid"),
            )

        try:
            self.validate_authz(self.payload)
        except (Exception, pydantic_ValidationError) as e:
            logger.warning(f"Authz request failed: {e}")
            return self.redirect_response_data(
                self.payload["redirect_uri"],
                error="invalid_request",
                error_description=_("Authorization request validation error"),
            )

        # stores the authz request in a hidden field in the form
        form = self.get_login_form()()
        context = {
            "client_organization_name": tc.metadata.get(
                "client_name", self.payload["client_id"]
            ),
            "hidden_form": AuthzHiddenForm(dict(authz_request_object=req)),
            "form": form
        }
        return render(request, self.template, context)

    def post(self, request, *args, **kwargs):
        """
            When the User prompts his credentials
        """
        form = self.get_login_form()(request.POST)
        if not form.is_valid():
            return render(
                request,
                self.template,
                {
                    "form": form,
                    "hidden_form": AuthzHiddenForm(request.POST),
                }
            )

        authz_form = AuthzHiddenForm(request.POST)
        authz_form.is_valid()
        authz_request = authz_form.cleaned_data.get("authz_request_object")
        try:
            self.validate_authz_request_object(authz_request)
        except Exception as e:
            logger.error(
                "Authz request object validation failed "
                f"for {authz_request}: {e} "
            )
            # we don't have a redirect_uri here
            return HttpResponseForbidden()

        # autenticate the user
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(username=username, password=password)
        if not user:
            errors = form._errors.setdefault("username", ErrorList())
            errors.append(_("invalid username or password"))
            return render(
                request,
                self.template,
                {
                    "form": form,
                    "hidden_form": AuthzHiddenForm(request.POST),
                }
            )
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
        url = reverse("oidc_provider_consent")
        if (
                user.is_staff and
                'spid_cie_oidc.relying_party_test' in settings.INSTALLED_APPS
        ):
            try:
                url = reverse("oidc_provider_staff_testing")
            except Exception as e:
                logger.error(f"testigng page url reverse failed: {e}")

        return HttpResponseRedirect(url)


class ConsentPageView(OpBase, View):

    template = "op_user_consent.html"

    def get_consent_form(self):
        return ConsentPageForm

    def get(self, request, *args, **kwargs):
        try:
            session = self.check_session(request)
        except Exception:
            logger.warning("Invalid session on Consent page")
            return HttpResponseForbidden()

        tc = TrustChain.objects.filter(
            sub=session.client_id,
            type="openid_relying_party",
            is_active = True
        ).first()

        # if this auth code was already been used ... forbidden
        if IssuedToken.objects.filter(session=session):
            logger.warning(f"Auth code Replay {session}")
            return HttpResponseForbidden()

        i18n_user_claims = self.attributes_names_to_release(
            request, session
        )['i18n_user_claims']

        context = {
            "form": self.get_consent_form()(),
            "session": session,
            "client_organization_name": tc.metadata.get(
                "client_name", session.client_id
            ),
            "user_claims": sorted(set(i18n_user_claims),)
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
                self.payload["redirect_uri"],
                # TODO: this is not normative -> check AgID/IPZS
                error="rejected_by_user",
                error_description=_("User rejected the release of attributes"),
            )
        issuer = self.get_issuer()

        iss_token_data = self.get_iss_token_data(session, issuer)
        IssuedToken.objects.create(**iss_token_data)

        return self.redirect_response_data(
            self.payload["redirect_uri"],
            code=session.auth_code,
            state=session.authz_request["state"],
            iss=issuer.sub if issuer else "",
        )


@method_decorator(csrf_exempt, name="dispatch")
class TokenEndpoint(OpBase, View):

    def get(self, request, *args, **kwargs):
        return HttpResponseBadRequest()

    def grant_auth_code(self, request, *args, **kwargs):
        """
            Token request for an authorization code grant
        """
        # PKCE check - based on authz.authz_request["code_challenge_method"] == S256
        code_challenge = hashlib.sha256(request.POST["code_verifier"].encode()).digest()
        code_challenge = base64.urlsafe_b64encode(code_challenge).decode("utf-8")
        code_challenge = code_challenge.replace("=", "")
        if code_challenge != self.authz.authz_request["code_challenge"]:
            return HttpResponseForbidden()
        #

        issued_token = IssuedToken.objects.filter(
            session= self.authz,
            revoked = False
        ).first()

        jwk_at = unpad_jwt_payload(issued_token.access_token)
        expires_in = self.get_expires_in(jwk_at['iat'], jwk_at['exp'])

        iss_token_data = dict( # nosec B106
            access_token = issued_token.access_token,
            id_token = issued_token.id_token,
            token_type = "Bearer", # nosec B106
            expires_in = expires_in,
            # TODO: remove unsupported scope
            scope = self.authz.authz_request["scope"],
        )
        if issued_token.refresh_token:
            iss_token_data['refresh_token'] = issued_token.refresh_token

        return JsonResponse(iss_token_data)

    def is_token_renewable(self, session) -> bool:
        issuedToken = IssuedToken.objects.filter(
            session = session
        )
        return (issuedToken.count() - 1) < getattr(settings, "OIDCFED_PROVIDER_MAX_REFRESH", 1)

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
        issued_token = IssuedToken.objects.filter(
            refresh_token = request.POST['refresh_token'],
            revoked = False
        ).first()

        if not issued_token:
            return JsonResponse(
                {
                    "error": "invalid_request",
                    "error_description": "Refresh token not found",

                },
                status = 400
            )

        session = issued_token.session
        if not self.is_token_renewable(session):
            return JsonResponse(
                    {
                        "error": "invalid_request",
                        "error_description": "Refresh Token can no longer be updated",

                    }, status = 400
            )
        iss_token_data = self.get_iss_token_data(session, self.get_issuer())
        IssuedToken.objects.create(**iss_token_data)
        issued_token.revoked = True
        issued_token.save()

        jwk_at = unpad_jwt_payload(iss_token_data['access_token'])
        expires_in = self.get_expires_in(jwk_at['iat'], jwk_at['exp'])

        data = dict( # nosec B106
            access_token = iss_token_data['access_token'],
            id_token = iss_token_data['id_token'],
            token_type = "Bearer", # nosec B106
            expires_in = expires_in,
            # TODO: remove unsupported scope
            scope = self.authz.authz_request["scope"],
        )
        if issued_token.refresh_token:
            data['refresh_token'] = issued_token.refresh_token

        return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        logger.debug(f"{request.headers}: {request.POST}")

        result = self.validate_json_schema(
            request.POST.dict(),
            request.POST["grant_type"],
            "Token request object validation failed "
        )
        if result:
            return result

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
                    'error': "unauthorized_client",
                    'error_description': ""

                }, status = 403
            )
        if request.POST.get("grant_type") == 'authorization_code':
            return self.grant_auth_code(request)
        elif request.POST.get("grant_type") == 'refresh_token':
            return self.grant_refresh_token(request)
        else:
            # Token exchange? :-)
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
            token.session.authz_request.get(
                "claims", {}
            ).get("userinfo", {}).keys()
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
        result = self.validate_json_schema(
            request.POST.dict(),
            "revocation_request",
            "Revocation request object validation failed "
        )
        if result:
            return result
        try:
            self.check_client_assertion(
                request.POST['client_id'],
                request.POST['client_assertion']
            )
        except Exception:
            return JsonResponse(
                {
                    "error": "invalid_request",
                    "error_description": "Validation of client assertion failed",

                },
                status = 400
            )

        access_token = request.POST.get('token', None)
        if not access_token:
            return JsonResponse(
                {
                    "error": "invalid_request",
                    "error_description": "The request does not include Access Token",

                },
                status = 400
            )

        token = IssuedToken.objects.filter(
            access_token= access_token,
            revoked = False
        ).first()

        if not token or token.expired:
            return JsonResponse(
                {
                    "error": "invalid_grant",
                    "error_description": "Access Token not found or expired",

                },
                status = 400
            )

        if token.is_revoked:
            return JsonResponse(
                {
                    "error": "invalid_grant",
                    "error_description": "Access Token revoked",
                },
                status = 400
            )

        token.session.revoke()
        return HttpResponse()


class IntrospectionEndpoint(OpBase, View):
    def get(self, request, *args, **kwargs):
        return HttpResponseBadRequest()

    def post(self, request, *args, **kwargs):
        result = self.validate_json_schema(
            request.POST.dict(),
            "introspection_request",
            "Introspection request object validation failed"
        )
        if result:
            return result
        client_id = request.POST['client_id']
        try:
            self.check_client_assertion(
                client_id,
                request.POST['client_assertion']
            )
        except Exception:
            return HttpResponseForbidden()
        required_token = request.POST['token']
        # query con client_id, access token
        token = IssuedToken.objects.filter(
            access_token=required_token
        ).first()
        session = token.session
        if session.client_id != client_id:
            return JsonResponse(
                error = "invalid_client",
                error_description = "Client not recognized"
            )
        active = token and not token.is_revoked and not token.expired
        exp = token.expires
        sub = token.session.client_id
        issuer = self.get_issuer()
        iss = issuer.sub
        authz_request = session.authz_request
        scope = authz_request["scope"]
        response = {
            "active": active,
            "exp": exp,
            "sub" : sub,
            "iss": iss,
            "client_id": client_id,
            "aud": [client_id],
            "scope": scope
        }
        return JsonResponse(response)


def oidc_provider_not_consent(request):
    logout(request)
    urlrp = reverse("spid_cie_rp_callback")
    kwargs = dict(
        error = "invalid_request",
        error_description = _(
            "Authentication request rejected by user"
        )
    )
    url = f'{urlrp}?{urllib.parse.urlencode(kwargs)}'
    return HttpResponseRedirect(url)
