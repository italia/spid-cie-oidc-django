import json
import logging

from django.conf import settings
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.views import View
from django.shortcuts import render
from django.utils import timezone
from django.utils.module_loading import import_string
from django.utils.translation import gettext as _

from . import OAuth2BaseView
from .exceptions import MisconfiguredClientIssuer
from .oauth2 import *
from .oidc import *
from .models import OidcAuthentication
from .utils import (
    http_dict_to_redirect_uri_path,
    http_redirect_uri_to_dict,
    random_string,
)


logger = logging.getLogger(__name__)


class SpidCieOidcRpBeginView(View):
    """View which processes the actual Authz request and
    returns a Http Redirect
    """

    def get_federation_trust(self, request):
        """
        OIDC Federation Metadata discovery for a given sub/issuer_id
        """
        # TODO
        available_issuers = {}
        available_issuers_len = len(available_issuers)

        # todo: validate it upoun a schema
        sub = request.GET.get("sub")

        if not sub:
            if available_issuers_len > 1:
                # TODO - a provider selection page here!
                raise NotImplementedError()

            elif available_issuers_len == 1:
                issuer_id = list(available_issuers.keys())[0]
            else:
                raise MisconfiguredClientIssuer("No available issuers found")
        return issuer_id, available_issuers[issuer_id]["issuer"]

    def get(self, request, *args, **kwargs):
        """
        https://tools.ietf.org/html/rfc6749#section-4.1.1

        https://login.agid.gov.it/.well-known/openid-configuration
        http://localhost:8888/oidc/spid/begin?issuer_id=agid_login_local
        """
        issuer_id, issuer_fqdn = self.get_oidc_rp_issuer(request)
        client_conf = settings.JWTCONN_RP_CLIENTS[issuer_id]

        try:
            provider_conf = self.provider_discovery(client_conf)
        except Exception as e:  # pragma: no cover
            _msg = f"Failed to get provider discovery from {issuer_fqdn}"
            logger.error(f"{_msg}: {e}")
            return HttpResponseBadRequest(_(_msg))

        try:
            jwks_dict, jwks = self.get_jwks_from_jwks_uri(
                provider_conf["jwks_uri"], verify=client_conf["httpc_params"]["verify"]
            )
        except Exception as e:  # pragma: no cover
            _msg = f"Failed to get jwks from {issuer_fqdn}"
            logger.error(f"{_msg}: {e}")
            return HttpResponseBadRequest(_(_msg))

        client_prefs = client_conf["client_preferences"]
        authz_endpoint = provider_conf["authorization_endpoint"]
        authz_data = dict(
            scope=" ".join(client_prefs["scope"]),
            redirect_uri=client_conf["redirect_uris"][0],
            response_type=client_prefs["response_types"][0],
            nonce=random_string(24),
            state=random_string(32),
            client_id=client_conf["client_id"],
            endpoint=authz_endpoint,
        )

        # TODO: generalized addons loader
        has_pkce = client_conf.get("add_ons", {}).get("pkce")
        if has_pkce:
            pkce_func = import_string(has_pkce["function"])
            pkce_values = pkce_func(**has_pkce["kwargs"])
            authz_data.update(pkce_values)

        # create request in db
        authz_entry = dict(
            client_id=client_conf["client_id"],
            state=authz_data["state"],
            endpoint=authz_endpoint,
            issuer=issuer_fqdn,
            issuer_id=issuer_id,
            data=json.dumps(authz_data),
            provider_jwks=json.dumps(jwks_dict),
            provider_configuration=json.dumps(provider_conf),
        )
        OidcAuthentication.objects.create(**authz_entry)

        authz_data.pop("code_verifier")
        uri_path = http_dict_to_redirect_uri_path(authz_data)
        url = "?".join((authz_endpoint, uri_path))
        data = http_redirect_uri_to_dict(url)
        logger.debug(f"Started Authz: {url}")
        logger.debug(f"Authorization Request data: {data}")
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
        authz = OidcAuthentication.objects.filter(
            state=request_args.get("state"),
        )
        if not authz:
            return HttpResponseBadRequest(_("Unsolicited response"))
        else:
            authz = authz.last()

        authz_data = json.loads(authz.data)
        provider_conf = authz.get_provider_configuration()
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
    def get(self, request):
        data = {"oidc_rp_user_attrs": request.session["oidc_rp_user_attrs"]}
        return render(request, "echo_attributes.html", data)


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
    return render(request, "rp_landing.html")
