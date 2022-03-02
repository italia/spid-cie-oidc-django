import json
import logging

from copy import deepcopy
from django.conf import settings
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponseBadRequest, HttpResponseRedirect, Http404
from django.http import HttpResponseForbidden
from django.views import View
from django.shortcuts import render
from django.utils import timezone
from django.utils.module_loading import import_string
from django.utils.translation import gettext as _

from spid_cie_oidc.entity.models import (
    FederationEntityConfiguration,
    TrustChain
)
from spid_cie_oidc.entity.jwtse import create_jws
from spid_cie_oidc.entity.statements import get_http_url
from spid_cie_oidc.entity.settings import HTTPC_PARAMS
from spid_cie_oidc.entity.trust_chain_operations import get_or_create_trust_chain
from spid_cie_oidc.onboarding.schemas.authn_requests import AcrValuesSpid

from . import OAuth2BaseView
from .oauth2 import *
from .oidc import *
from .models import OidcAuthentication, OidcAuthenticationToken
from .utils import (
    http_dict_to_redirect_uri_path,
    http_redirect_uri_to_dict,
    random_string,
)
from . settings import RP_PKCE_CONF, RP_PROVIDER_PROFILES

logger = logging.getLogger(__name__)


class SpidCieOidcRp:
    """
        Baseclass with common methods for RPs
    """

    def get_jwks_from_jwks_uri(
        self,
        jwks_uri:str
    ) -> dict:
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
            return HttpResponseBadRequest(
                f"Missing provider url. "
                "Please try '?provider=https://provider-subject/'"
            )

        trust_anchor = request.GET.get(
            "trust_anchor", settings.OIDCFED_TRUST_ANCHOR
        )
        if trust_anchor not in settings.OIDCFED_TRUST_ANCHORS:
            return HttpResponseBadRequest(
                f"Unallowed Trust Anchor"
            )

        tc = TrustChain.objects.filter(
            sub = request.GET["provider"],
            trust_anchor__sub = trust_anchor,
        ).first()

        if not tc:
            logger.info(
                f'Trust Chain not found for {request.GET["provider"]}'
            )
        elif not tc.is_active:
            logger.warning(
                f"{tc} found but DISABLED at {tc.modified}"
            )
            raise Http404("provider metadata not found.")
        elif tc.is_expired:
            logger.warning(
                f"{tc} found but expired at {tc.exp}"
            )
            logger.warning("We should try to renew the trust chain")
            tc = get_or_create_trust_chain(
                    subject = tc.sub,
                    trust_anchor = trust_anchor,
                    # TODO
                    # required_trust_marks: list = [],
                    metadata_type = "openid_provider",
                    force = True
            )
        return tc


class SpidCieOidcRpBeginView(SpidCieOidcRp, View):
    """View which processes the actual Authz request and
    returns a Http Redirect
    """

    def get(self, request, *args, **kwargs):
        """
            http://localhost:8001/oidc/rp/authorization?
            provider=http://127.0.0.1:8002/
        """
        tc = self.get_oidc_op(request)
        if not tc:
            raise Http404("Trust Chain is unavailable.")
        provider_metadata = tc.metadata
        if not provider_metadata:
            raise Http404("provider metadata not found.")

        entity_conf = FederationEntityConfiguration.objects.filter(
            entity_type = "openid_relying_party",
            # TODO: RPs multitenancy?
            # sub = request.build_absolute_uri()
        ).first()
        if not entity_conf:
            raise Http404("Missing configuration.")

        client_conf = entity_conf.metadata['openid_relying_party']

        if not (
            provider_metadata.get("jwks_uri", None) or
            provider_metadata.get("jwks", None)
        ):
            raise HttpResponseForbidden("Invalid provider Metadata")

        if provider_metadata.get("jwks", None):
            jwks_dict = provider_metadata["jwks"]
        else:
            jwks_dict = self.get_jwks_from_jwks_uri(
                provider_metadata["jwks_uri"]
            )
        if not jwks_dict:
            _msg = f"Failed to get jwks from {tc.sub}"
            logger.error(f"{_msg}:")
            return HttpResponseBadRequest(_(_msg))

        authz_endpoint = provider_metadata["authorization_endpoint"]

        redirect_uri = request.GET.get(
            "redirect_uri", client_conf["redirect_uris"][0]
        )
        if redirect_uri not in client_conf["redirect_uris"]:
            redirect_uri = client_conf["redirect_uris"][0]

        authz_data = dict(
            scope=" ".join([i for i in request.GET.get("scope", ["openid"])]),
            redirect_uri=redirect_uri,
            response_type=client_conf["response_types"][0],
            nonce=random_string(32),
            state=random_string(32),
            client_id=client_conf["client_id"],
            endpoint=authz_endpoint,
            acr_values = request.GET.get(
                "acr_values", AcrValuesSpid.l2.value

            ),
            aud = [tc.sub, authz_endpoint]
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
            issuer=tc.sub,
            issuer_id=tc.sub,
            data=json.dumps(authz_data),
            provider_jwks=json.dumps(jwks_dict),
            provider_configuration=json.dumps(provider_metadata)
        )

        # TODO: Prune the old or unbounded authz ...
        OidcAuthentication.objects.create(**authz_entry)

        authz_data.pop("code_verifier")
        # add the signed request object
        authz_data_obj = deepcopy(authz_data)
        authz_data_obj["iss"] = client_conf['client_id']
        authz_data_obj["sub"] = client_conf['client_id']
        request_obj = create_jws(
            authz_data_obj, entity_conf.jwks[0]
        )
        authz_data["request"] = request_obj
        uri_path = http_dict_to_redirect_uri_path(authz_data)
        url = "?".join((authz_endpoint, uri_path))
        data = http_redirect_uri_to_dict(url)
        logger.info(f"Starting Authz request to {url}")
        return HttpResponseRedirect(url)


class SpidCieOidcRpCallbackView(
    OAuth2BaseView, View, OidcUserInfo, OAuth2AuthorizationCodeGrant
):
    """
    View which processes an Authorization Response
    https://tools.ietf.org/html/rfc6749#section-4.1.2

    eg:
    /redirect_uri?code=tYkP854StRqBVcW4Kg4sQfEN5Qz&state=R9EVqaazGsj3wg5JgxIgm8e8U4BMvf7W


    """

    error_template = "rp_error.html"

    def process_user_attributes(
        self, userinfo: dict, client_conf: dict, authz: OidcAuthentication
    ):
        user_map = client_conf["user_attributes_map"]
        data = dict()
        for k, v in user_map.items():
            for i in v:
                if isinstance(i, str):
                    if i in userinfo:
                        data[k] = userinfo[i]
                        break

                elif isinstance(i, dict):
                    args = (userinfo, client_conf, authz.__dict__, i["kwargs"])
                    value = import_string(i["func"])(*args)
                    if value:
                        data[k] = value
                        break
        return data

    def user_reunification(self, user_attrs: dict, client_conf: dict):
        user_model = get_user_model()
        field_name = client_conf["user_lookup_field"]
        lookup = {field_name: user_attrs[field_name]}
        user = user_model.objects.filter(**lookup)
        if user:  # pragma: no cover
            user = user.first()
            logger.info(f"{field_name} matched on user {user}")
            return user
        elif client_conf.get("user_create"):
            user = user_model.objects.create(**user_attrs)
            logger.info(f"Created new user {user}")
            return user

    def get(self, request, *args, **kwargs):
        """
        docs here
        """
        request_args = {k: v for k, v in request.GET.items()}

        # TODO
        # breakpoint()
        if 'error' in request_args:
            return render(request, self.error_template, request_args)

        authz = OidcAuthentication.objects.filter(
            state=request_args.get("state"),
        )
        if not authz:
            return HttpResponseBadRequest(_("Unsolicited response"))
        else:
            authz = authz.last()

        authz_data = json.loads(authz.data)
        provider_conf = authz.get_provider_configuration()

        # TODO: get Trust Chain from response and match to the state of
        # the preexisting OidcAuthentication on the DB
        client_conf = settings.JWTCONN_RP_CLIENTS[authz.issuer_id]

        code = request.GET.get("code")
        authz_token = OidcAuthenticationToken.objects.create(
            authz_request=authz, code=code
        )

        token_request = self.access_token_request(
            redirect_uri=authz_data["redirect_uri"],
            client_id=authz.client_id,
            state=authz.state,
            code=code,
            issuer_id=authz.issuer_id,
            client_conf=client_conf,
            token_endpoint_url=provider_conf["token_endpoint"],
            code_verifier=authz_data.get("code_verifier"),
        )

        if not token_request:
            return HttpResponseBadRequest(
                _("Authentication token seems not to be valid.")
            )

        keyjar = authz.get_provider_keyjar()

        if not self.validate_jwt(authz, token_request["access_token"], keyjar):
            pass
            # Actually AgID Login have a non-JWT access token!
            # return HttpResponseBadRequest(
            # _('Authentication response validation error.')
            # )
        if not self.validate_jwt(authz, token_request["id_token"], keyjar):
            return HttpResponseBadRequest(_("Authentication token validation error."))

        # just for debugging purpose ...
        decoded_id_token = self.decode_jwt(
            "ID Token", authz, token_request["id_token"], keyjar
        )
        logger.debug(decoded_id_token)
        decoded_access_token = self.decode_jwt(
            "Access Token", authz, token_request["access_token"], keyjar
        )
        logger.debug(decoded_access_token)

        authz_token.access_token = token_request["access_token"]
        authz_token.id_token = token_request["id_token"]
        authz_token.scope = token_request.get("scope")
        authz_token.token_type = token_request["token_type"]
        authz_token.expires_in = token_request["expires_in"]
        authz_token.save()

        userinfo = self.get_userinfo(
            authz.state,
            authz_token.access_token,
            provider_conf,
            verify=client_conf["httpc_params"]["verify"],
        )
        if not userinfo:
            return HttpResponseBadRequest(_("UserInfo response seems not to be valid."))

        # here django user attr mapping
        user_attrs = self.process_user_attributes(userinfo, client_conf, authz)
        if not user_attrs:
            _msg = "No user attributes have been processed"
            logger.warning(f"{_msg}: {userinfo}")
            raise PermissionDenied(_msg)
        user = self.user_reunification(user_attrs, client_conf)
        if not user:
            raise PermissionDenied()

        # authenticate the user
        login(request, user)
        request.session["oidc_rp_user_attrs"] = user_attrs
        authz_token.user = user
        authz_token.save()

        return HttpResponseRedirect(
            client_conf.get("login_redirect_url")
            or getattr(settings, "LOGIN_REDIRECT_URL")
        )


class SpidCieOidcRpCallbackEchoAttributes(View):
    template = "echo_attributes.html"

    def get(self, request):
        data = {"oidc_rp_user_attrs": request.session["oidc_rp_user_attrs"]}
        return render(request, self.template, data)


@login_required
def oidc_rpinitiated_logout(request):
    """
    http://localhost:8000/end-session/?id_token_hint=
    """
    auth_tokens = OidcAuthenticationToken.objects.filter(user=request.user).filter(
        Q(logged_out__iexact="") | Q(logged_out__isnull=True)
    )
    authz = auth_tokens.last().authz_request
    provider_conf = authz.get_provider_configuration()
    end_session_url = provider_conf.get("end_session_endpoint")

    # first of all on RP side ...
    logout(request)

    if not end_session_url:
        logger.warning(f"{authz.issuer_url} does not support end_session_endpoint !")
        return HttpResponseRedirect(settings.LOGOUT_REDIRECT_URL)
    else:
        auth_token = auth_tokens.last()
        url = f"{end_session_url}?id_token_hint={auth_token.id_token}"
        auth_token.logged_out = timezone.localtime()
        auth_token.save()
        return HttpResponseRedirect(url)


def oidc_rp_landing(request):
    trust_chains = TrustChain.objects.filter(type="openid_provider")
    providers = []
    for tc in trust_chains:
        if tc.is_valid:
            providers.append(tc)
    content = {"providers": providers}
    return render(request, "rp_landing.html", content)
