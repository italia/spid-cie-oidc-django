import json
import logging
from copy import deepcopy
import random

import requests
from django.conf import settings
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.utils.module_loading import import_string
from django.utils.translation import gettext as _
from django.views import View
from pydantic import ValidationError
from spid_cie_oidc.entity.exceptions import InvalidTrustchain
from spid_cie_oidc.entity.jwtse import (
    create_jws,
    unpad_jwt_head,
    unpad_jwt_payload,
    verify_jws
)
from spid_cie_oidc.entity.models import (FederationEntityConfiguration,
                                         TrustChain)
from spid_cie_oidc.entity.settings import HTTPC_PARAMS
from spid_cie_oidc.entity.statements import get_http_url
from spid_cie_oidc.entity.trust_chain_operations import get_or_create_trust_chain
from spid_cie_oidc.onboarding.schemas.authn_requests import AcrValuesSpid
from spid_cie_oidc.relying_party.settings import (
    RP_DEFAULT_PROVIDER_PROFILES,
    RP_PROVIDER_PROFILES
)

from .models import OidcAuthentication, OidcAuthenticationToken
from .oauth2 import *
from .oidc import *
from .settings import (
    RP_ATTR_MAP,
    RP_PKCE_CONF,
    RP_REQUEST_CLAIM_BY_PROFILE,
    RP_USER_CREATE,
    RP_USER_LOOKUP_FIELD,
)
from .utils import (
    http_dict_to_redirect_uri_path,
    process_user_attributes,
    random_string,
)

logger = logging.getLogger(__name__)


class SpidCieOidcRp:
    """
    Baseclass with common methods for RPs
    """

    def get_jwks_from_jwks_uri(self, jwks_uri: str) -> dict:
        """
        get jwks
        """
        try:
            jwks_dict = get_http_url([jwks_uri], httpc_params=HTTPC_PARAMS).json()
        except Exception as e:
            logger.error(f"Failed to download jwks from {jwks_uri}: {e}")
            return {}
        return jwks_dict

    def get_oidc_op(self, request) -> TrustChain:
        """
            get available trust to a specific OP
        """
        if not request.GET.get("provider", None):
            logger.warning(
                "Missing provider url. Please try '?provider=https://provider-subject/'"
            )
            raise InvalidTrustchain(
                "Missing provider url. Please try '?provider=https://provider-subject/'"
            )

        trust_anchor = request.GET.get(
            "trust_anchor",
            settings.OIDCFED_IDENTITY_PROVIDERS.get(
                request.GET["provider"],
                settings.OIDCFED_DEFAULT_TRUST_ANCHOR
            )
        )

        if trust_anchor not in settings.OIDCFED_TRUST_ANCHORS:
            logger.warning("Unallowed Trust Anchor")
            raise InvalidTrustchain("Unallowed Trust Anchor")

        tc = TrustChain.objects.filter(
            sub=request.GET["provider"],
            trust_anchor__sub=trust_anchor,
        ).first()

        discover_trust = False
        if not tc:
            logger.info(f'Trust Chain not found for {request.GET["provider"]}')
            discover_trust = True

        elif not tc.is_active:
            logger.warning(f"{tc} found but DISABLED at {tc.modified}")
            raise InvalidTrustchain(f"{tc} found but DISABLED at {tc.modified}")

        elif tc.is_expired:
            logger.warning(f"{tc} found but expired at {tc.exp}")
            logger.warning("Try to renew the trust chain")
            discover_trust = True

        if discover_trust:
            tc = get_or_create_trust_chain(
                subject=request.GET["provider"],
                trust_anchor=trust_anchor,
                # TODO - not sure that it's required for a RP that fetches OP directly from TA
                # required_trust_marks = [],
                metadata_type="openid_provider",
                force=True,
            )
        return tc

    def validate_json_schema(self, request, schema_type, error_description):
        try:
            schema = RP_PROVIDER_PROFILES[RP_DEFAULT_PROVIDER_PROFILES]
            schema[schema_type](**request)
        except ValidationError as e:
            logger.error(
                f"{error_description} "
                f"for {request.get('client_id', None)}: {e} "
            )
            return JsonResponse(
                {
                    "error": "invalid_request",
                    "error_description": f"{error_description} ",
                }
            )


class SpidCieOidcRpBeginView(SpidCieOidcRp, View):
    """
        View which processes the actual Authz request and
        returns a Http Redirect
    """

    error_template = "rp_error.html"

    def get(self, request, *args, **kwargs):
        """
        http://localhost:8001/oidc/rp/authorization?
        provider=http://127.0.0.1:8002/
        """
        try:
            tc = self.get_oidc_op(request)
            if not tc:
                context = {
                    "error": "request rejected",
                    "error_description": "Trust Chain is unavailable.",
                }
                return render(request, self.error_template, context)

        except InvalidTrustchain as exc:
            context = {
                "error": "request rejected",
                "error_description": str(exc.args),
            }
            return render(request, self.error_template, context)

        except Exception as exc:
            context = {
                "error": "request rejected",
                "error_description": _(str(exc.args)),
            }
            return render(request, self.error_template, context)

        provider_metadata = tc.metadata
        if not provider_metadata:
            context = {
                "error": "request rejected",
                "error_description": _("provider metadata not found"),
            }
            return render(request, self.error_template, context)

        entity_conf = FederationEntityConfiguration.objects.filter(
            entity_type="openid_relying_party",
            # TODO: RPs multitenancy?
            # sub = request.build_absolute_uri()
        ).first()

        if not entity_conf:
            context = {
                "error": "request rejected",
                "error_description": _("Missing configuration."),
            }
            return render(request, self.error_template, context)

        client_conf = entity_conf.metadata["openid_relying_party"]
        if not (
            provider_metadata.get("jwks_uri", None)
            or provider_metadata.get("jwks", None)
        ):
            context = {
                "error": "request rejected",
                "error_description": _("Invalid provider Metadata."),
            }
            return render(request, self.error_template, context)

        if provider_metadata.get("jwks", None):
            jwks_dict = provider_metadata["jwks"]
        else:
            jwks_dict = self.get_jwks_from_jwks_uri(provider_metadata["jwks_uri"])
        if not jwks_dict:
            _msg = f"Failed to get jwks from {tc.sub}"
            logger.error(_msg)
            context = {
                "error": "request rejected",
                "error_description": _msg
            }
            return render(request, self.error_template, context)

        authz_endpoint = provider_metadata["authorization_endpoint"]

        redirect_uri = request.GET.get("redirect_uri", client_conf["redirect_uris"][0])
        if redirect_uri not in client_conf["redirect_uris"]:
            logger.warning(
                f"Requested for unknown redirect uri {redirect_uri}. "
                f"Reverted to default {client_conf['redirect_uris'][0]}."
            )
            redirect_uri = client_conf["redirect_uris"][0]

        authz_data = dict(
            scope= request.GET.get("scope", None) or "openid",
            redirect_uri=redirect_uri,
            response_type=client_conf["response_types"][0],
            nonce=random_string(32),
            state=random_string(32),
            client_id=client_conf["client_id"],
            endpoint=authz_endpoint,
            acr_values=request.GET.get("acr_values", AcrValuesSpid.l2.value),
            iat=int(timezone.localtime().timestamp()),
            aud=[tc.sub, authz_endpoint],
            claims=RP_REQUEST_CLAIM_BY_PROFILE[request.GET.get("profile", "spid")],
        )

        _prompt = request.GET.get("prompt", "consent login")

        # if "offline_access" in authz_data["scope"]:
        # _prompt.extend(["consent login"])

        authz_data["prompt"] = _prompt

        # PKCE
        pkce_func = import_string(RP_PKCE_CONF["function"])
        pkce_values = pkce_func(**RP_PKCE_CONF["kwargs"])
        authz_data.update(pkce_values)
        #
        authz_entry = dict(
            client_id=client_conf["client_id"],
            state=authz_data["state"],
            endpoint=authz_endpoint,
            # TODO: better have here an organization name
            provider=tc.sub,
            provider_id=tc.sub,
            data=json.dumps(authz_data),
            provider_jwks=json.dumps(jwks_dict),
            provider_configuration=provider_metadata,
        )

        # TODO: Prune the old or unbounded authz ...
        OidcAuthentication.objects.create(**authz_entry)

        authz_data.pop("code_verifier")
        # add the signed request object
        authz_data_obj = deepcopy(authz_data)
        authz_data_obj["iss"] = client_conf["client_id"]
        authz_data_obj["sub"] = client_conf["client_id"]

        request_obj = create_jws(authz_data_obj, entity_conf.jwks[0])
        authz_data["request"] = request_obj
        uri_path = http_dict_to_redirect_uri_path(authz_data)
        url = "?".join((authz_endpoint, uri_path))
        logger.info(f"Starting Authz request to {url}")
        return HttpResponseRedirect(url)


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

    def get_jwk_from_jwt(self, jwt: str, provider_jwks: dict) -> dict:
        """
            docs here
        """
        head = unpad_jwt_head(jwt)
        kid = head["kid"]
        for jwk in provider_jwks:
            if jwk["kid"] == kid:
                return jwk
        return {}

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
        result = self.validate_json_schema(
            request.GET.dict(),
            "authn_response",
            "Authn response object validation failed"
        )
        if result:
            return result

        if not authz:
            # TODO: verify error message and status
            context = {
                "error": "unauthorized request",
                "error_description": _("Authentication not found"),
            }
            return render(request, self.error_template, context, status=401)
        else:
            authz = authz.last()

        code = request.GET.get("code")
        if not code:
            # TODO: verify error message and status
            context = {
                "error": "invalid request",
                "error_description": _("Request MUST contain code"),
            }
            return render(request, self.error_template, context, status=400)

        authz_token = OidcAuthenticationToken.objects.create(
            authz_request=authz, code=code
        )
        self.rp_conf = FederationEntityConfiguration.objects.get(
            sub=authz_token.authz_request.client_id
        )
        if not self.rp_conf:
            # TODO: verify error message and status
            context = {
                "error": "invalid request",
                "error_description": _("Relay party not found"),
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
            # TODO: verify error message
            context = {
                "error": "invalid token response",
                "error_description": _("Token response seems not to be valid"),
            }
            return render(request, self.error_template, context, status=400)

        else:
            result = self.validate_json_schema(
                token_response,
                "token_response",
                "Token response object validation failed"
            )
            if result:
                return result

        entity_conf = FederationEntityConfiguration.objects.filter(
            entity_type="openid_provider",
        ).first()

        op_conf = entity_conf.metadata["openid_provider"]
        jwks = op_conf["jwks"]["keys"]
        access_token = token_response["access_token"]
        id_token = token_response["id_token"]
        op_ac_jwk = self.get_jwk_from_jwt(access_token, jwks)
        op_id_jwk = self.get_jwk_from_jwt(id_token, jwks)

        if not op_ac_jwk or not op_id_jwk:
            # TODO: verify error message and status
            context = {
                "error": "invalid token",
                "error_description": _("Authentication token seems not to be valid."),
            }
            return render(request, self.error_template, context, status=403)

        try:
            verify_jws(access_token, op_ac_jwk)
        except Exception:
            # TODO: verify error message
            context = {
                "error": "token verification failed",
                "error_description": _("Authentication token validation error."),
            }
            return render(request, self.error_template, context, status=403)

        try:
            verify_jws(id_token, op_id_jwk)
        except Exception:
            # TODO: verify error message
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
            verify=HTTPC_PARAMS,
        )
        if not userinfo:
            # TODO: verify error message
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


class SpidCieOidcRpCallbackEchoAttributes(View):
    template = "echo_attributes.html"

    def get(self, request):
        data = {"oidc_rp_user_attrs": request.session.get("oidc_rp_user_attrs", {})}
        return render(request, self.template, data)


@login_required
def oidc_rpinitiated_logout(request):
    """
        Call the token revocation endpoint of the op
    """
    auth_tokens = OidcAuthenticationToken.objects.filter(
        user=request.user
    ).filter(revoked__isnull=True)

    default_logout_url = getattr(
        settings, "LOGOUT_REDIRECT_URL", None
    ) or reverse("spid_cie_rp_landing")
    if not auth_tokens:
        logger.warning(
            "Token revocation failed: not found any authentication session"
        )
        return HttpResponseRedirect(default_logout_url)

    auth_token = auth_tokens.last()
    authz = auth_token.authz_request
    provider_conf = authz.provider_configuration
    revocation_endpoint_url = provider_conf.get("revocation_endpoint")

    # first of all on RP side ...
    logger.info(f"{request.user} logout")
    logout(request)
    if not revocation_endpoint_url:
        logger.warning(
            f"{authz.provider_id} doesn't expose the token revocation endpoint."
        )
        return HttpResponseRedirect(default_logout_url)
    else:
        rp_conf = FederationEntityConfiguration.objects.filter(
            sub= authz.client_id,
            is_active=True,
        ).first()

        # private_key_jwt
        client_assertion = create_jws(
            {
                "iss": authz.client_id,
                "sub": authz.client_id,
                "aud": [revocation_endpoint_url],
                "iat": iat_now(),
                "exp": exp_from_now(),
                "jti": str(uuid.uuid4()),
            },
            jwk_dict=rp_conf.jwks[0],
        )

        auth_token.logged_out = timezone.localtime()
        auth_token.save()

        revocation_request = dict(
            token = auth_token.access_token,
            client_id = authz.client_id,
            client_assertion = client_assertion,
            client_assertion_type = "urn:ietf:params:oauth:client-assertion-type:jwt-bearer"
        )
        try:
            requests.post(revocation_endpoint_url, data = revocation_request)
        except Exception as e:
            logger.warning(f"Token revocation failed: {e}")
        auth_tokens.update(revoked = timezone.localtime())
        return HttpResponseRedirect(default_logout_url)


def oidc_rp_landing(request):
    trust_chains = TrustChain.objects.filter(
        type="openid_provider", is_active=True
    )
    providers = []
    for tc in trust_chains:
        if tc.is_valid:
            providers.append(tc)
    random.shuffle(providers)
    content = {"providers": providers}
    return render(request, "rp_landing.html", content)
