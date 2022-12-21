import json
import logging

from djagger.decorators import schema
from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views import View
from spid_cie_oidc.entity.jwtse import (
    unpad_jwt_payload,
    verify_jws
)
from spid_cie_oidc.entity.models import FederationEntityConfiguration
from spid_cie_oidc.entity.settings import HTTPC_PARAMS
from spid_cie_oidc.entity.utils import get_jwks, get_jwk_from_jwt
from spid_cie_oidc.relying_party.exceptions import ValidationException
from spid_cie_oidc.relying_party.settings import RP_PROVIDER_PROFILES, RP_DEFAULT_PROVIDER_PROFILES

from ..models import OidcAuthentication, OidcAuthenticationToken
from ..oauth2 import *
from ..oidc import *
from ..settings import (
    RP_ATTR_MAP,
    RP_USER_CREATE,
    RP_USER_LOOKUP_FIELD,
)
from ..utils import process_user_attributes

from . import SpidCieOidcRp

logger = logging.getLogger(__name__)

schema_profile = RP_PROVIDER_PROFILES[RP_DEFAULT_PROVIDER_PROFILES]


@schema(
    summary="OIDC Relying Party auth code Callback",
    methods=['GET'],
    request_schema={
        "application/x-www-form-urlencoded" : schema_profile["authn_response"],
    },
    external_docs = {
        "alt_text": "AgID SPID OIDC Guidelines",
        "url": "https://www.agid.gov.it/it/agenzia/stampa-e-comunicazione/notizie/2021/12/06/openid-connect-spid-adottate-linee-guida"
    },
    tags = ['Relying Party']
)
class SpidCieOidcRpCallbackView(View, SpidCieOidcRp, OidcUserInfo, OAuth2AuthorizationCodeGrant):
    """
        View which processes an Authorization Response
        https://tools.ietf.org/html/rfc6749#section-4.1.2

        eg:
        /redirect_uri?code=tYkP854StRqBVcW4Kg4sQfEN5Qz&state=R9EVqaazGsj3wg5JgxIgm8e8U4BMvf7W
    """

    error_template = "rp_error.html"

    def user_reunification(self, user_attrs: dict):
        user_model = get_user_model()
        lookup = {
            f"attributes__{RP_USER_LOOKUP_FIELD}": user_attrs[RP_USER_LOOKUP_FIELD]
        }
        user = user_model.objects.filter(**lookup).first()
        if user:
            user.attributes.update(user_attrs)
            user.save()
            logger.info(f"{RP_USER_LOOKUP_FIELD} matched on user {user}")
            return user
        elif RP_USER_CREATE:
            user = user_model.objects.create(
                username=user_attrs.get("username", user_attrs["sub"]),
                first_name=user_attrs.get("given_name", user_attrs["sub"]),
                last_name=user_attrs.get("family_name", user_attrs["sub"]),
                email=user_attrs.get("email", ""),
                attributes=user_attrs,
            )
            logger.info(f"Created new user {user}")
            return user

    def get(self, request, *args, **kwargs):
        """
            The Authorization callback, the redirect uri where the auth code lands
        """
        request_args = {k: v for k, v in request.GET.items()}
        if "error" in request_args:
            return render(
                request,
                self.error_template,
                request_args,
                status=401
            )
        authz = OidcAuthentication.objects.filter(
            state=request_args.get("state"),
        )
        try:
            self.validate_json_schema(
                request.GET.dict(),
                "authn_response",
                "Authn response object validation failed"
            )
        except ValidationException:
            return JsonResponse(
                {
                    "error": "invalid_request",
                    "error_description": "Authn response object validation failed",
                },
                status = 400
            )

        if not authz:
            context = {
                "error": "unauthorized request",
                "error_description": _("Authentication not found"),
            }
            return render(request, self.error_template, context, status=401)
        else:
            authz = authz.last()

        code = request.GET.get("code")
        # mixups attacks prevention
        if request.GET.get('iss', None):
            if request.GET['iss'] != authz.provider_id:
                context = {
                    "error": "invalid request",
                    "error_description": _(
                        "authn response validation failed: mixups attack prevention."
                    ),
                }
                return render(request, self.error_template, context, status=400)

        authz_token = OidcAuthenticationToken.objects.create(
            authz_request=authz, code=code
        )
        self.rp_conf = FederationEntityConfiguration.objects.filter(
            sub=authz_token.authz_request.client_id
        ).first()
        if not self.rp_conf:
            context = {
                "error": "invalid request",
                "error_description": _("Relying party not found"),
            }
            return render(request, self.error_template, context, status=400)

        authz_data = json.loads(authz.data)
        token_response = self.access_token_request(
            redirect_uri=authz_data["redirect_uri"],
            state=authz.state,
            code=code,
            issuer_id=authz.provider_id,
            client_conf=self.rp_conf,
            token_endpoint_url=authz.provider_configuration["token_endpoint"],
            audience=[authz.provider_id],
            code_verifier=authz_data.get("code_verifier"),
        )
        if not token_response:
            context = {
                "error": "invalid token response",
                "error_description": _("Token response seems not to be valid"),
            }
            return render(request, self.error_template, context, status=400)

        else:
            try:
                self.validate_json_schema(
                    token_response,
                    "token_response",
                    "Token response object validation failed"
                )
            except ValidationException:
                return JsonResponse(
                    {
                        "error": "invalid_request",
                        "error_description": "Token response object validation failed",
                    },
                    status = 400
                )
        jwks = get_jwks(authz.provider_configuration)
        access_token = token_response["access_token"]
        id_token = token_response["id_token"]
        op_ac_jwk = get_jwk_from_jwt(access_token, jwks)
        op_id_jwk = get_jwk_from_jwt(id_token, jwks)

        if not op_ac_jwk or not op_id_jwk:
            logger.warning(
                "Token signature validation error, "
                f"the tokens were signed with a different kid from: {jwks}."
            )
            context = {
                "error": "invalid_token",
                "error_description": _("Authentication token seems not to be valid."),
            }
            return render(request, self.error_template, context, status=403)

        try:
            verify_jws(access_token, op_ac_jwk)
        except Exception as e:
            logger.warning(
                f"Access Token signature validation error: {e} "
            )
            context = {
                "error": "token verification failed",
                "error_description": _("Authentication token validation error."),
            }
            return render(request, self.error_template, context, status=403)

        try:
            verify_jws(id_token, op_id_jwk)
        except Exception as e:
            logger.warning(
                f"ID Token signature validation error: {e} "
            )
            context = {
                "error": "token verification failed",
                "error_description": _("ID token validation error."),
            }
            return render(request, self.error_template, context, status=403)

        decoded_id_token = unpad_jwt_payload(id_token)
        logger.debug(decoded_id_token)

        decoded_access_token = unpad_jwt_payload(access_token)
        logger.debug(decoded_access_token)

        authz_token.access_token = access_token
        authz_token.id_token = id_token
        authz_token.scope = token_response.get("scope")
        authz_token.token_type = token_response["token_type"]
        authz_token.expires_in = token_response["expires_in"]
        authz_token.save()
        userinfo = self.get_userinfo(
            authz.state,
            authz_token.access_token,
            authz.provider_configuration,
            verify=HTTPC_PARAMS.get("connection", {}).get("ssl", True)
        )
        if not userinfo:
            logger.warning(
                "Userinfo request failed for state: "
                f"{authz.state} to {authz.provider_id}"
            )
            context = {
                "error": "invalid userinfo response",
                "error_description": _("UserInfo response seems not to be valid"),
            }
            return render(request, self.error_template, context, status=400)

        # here django user attr mapping
        user_attrs = process_user_attributes(userinfo, RP_ATTR_MAP, authz.__dict__)
        if not user_attrs:
            _msg = "No user attributes have been processed"
            logger.warning(f"{_msg}: {userinfo}")
            # TODO: verify error message and status
            context = {
                "error": "missing user attributes",
                "error_description": _(f"{_msg}: {userinfo}"),
            }
            return render(request, self.error_template, context, status=403)

        user = self.user_reunification(user_attrs)
        if not user:
            # TODO: verify error message and status
            context = {"error": _("No user found"), "error_description": _("")}
            return render(request, self.error_template, context, status=403)

        # authenticate the user
        login(request, user)
        request.session["oidc_rp_user_attrs"] = user_attrs
        authz_token.user = user
        authz_token.save()
        return HttpResponseRedirect(
            getattr(
                settings, "LOGIN_REDIRECT_URL", None
            ) or reverse("spid_cie_rp_echo_attributes")
        )
