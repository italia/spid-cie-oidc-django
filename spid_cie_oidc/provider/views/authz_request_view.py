import hashlib
import logging
import urllib.parse
import uuid
import json

from djagger.decorators import schema
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.forms.utils import ErrorList
from django.http import (
    HttpResponseBadRequest,
    HttpResponseForbidden,
    HttpResponseRedirect
)
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views import View
from spid_cie_oidc.entity.exceptions import InvalidEntityConfiguration
from spid_cie_oidc.provider.schemas.authn_requests import AcrValues
from spid_cie_oidc.provider.forms import AuthLoginForm, AuthzHiddenForm
from spid_cie_oidc.provider.models import OidcSession
from spid_cie_oidc.provider.exceptions import AuthzRequestReplay, InvalidRefreshRequestException, ValidationException
from spid_cie_oidc.provider.settings import (
    OIDCFED_DEFAULT_PROVIDER_PROFILE,
    OIDCFED_PROVIDER_PROFILES,
    OIDCFED_PROVIDER_PROFILES_DEFAULT_ACR
)
from . import OpBase
logger = logging.getLogger(__name__)


schema_profile = OIDCFED_PROVIDER_PROFILES[OIDCFED_DEFAULT_PROVIDER_PROFILE]


@schema(
    summary="OIDC Provider Authorization endpoint",
    methods=['GET', 'POST'],
    get_request_schema = {
        "application/x-www-form-urlencoded": schema_profile["authorization_request_doc"],
        "request object - jwt payload": schema_profile["authorization_request"]
    },
    post_response_schema= {
            "302":schema_profile["authorization_response"],
            "403": schema_profile["authorization_error_response"]
    },
    external_docs = {
        "alt_text": "AgID SPID OIDC Guidelines",
        "url": "https://www.agid.gov.it/it/agenzia/stampa-e-comunicazione/notizie/2021/12/06/openid-connect-spid-adottate-linee-guida"
    },
    tags = ['Provider']
)
class AuthzRequestView(OpBase, View):
    """
        View which processes the actual Authz request and
        returns a Http Redirect
    """

    template = "op_user_login.html"

    def string_to_list(self, payload, must_list):
        for i in must_list:
            if isinstance(payload.get(i, None), str):
                if ' ' in payload[i]:
                    payload[i] = payload[i].split(' ')
                else:
                    payload[i] = [payload[i]]
        return payload

    def validate_authz(self, payload: dict):

        must_list = ("scope", "acr_values")
        payload = self.string_to_list(payload, must_list)
        if (
            'offline_access' in payload['scope'] and
            'consent' not in payload['prompt']
        ):
            raise InvalidRefreshRequestException(
                "scope with offline_access without prompt = consent"
            )
        redirect_uri = payload.get("redirect_uri", "")
        p = urllib.parse.urlparse(redirect_uri)
        scheme_fqdn = f"{p.scheme}://{p.hostname}"
        if payload.get("client_id", None) in scheme_fqdn:
            raise ValidationException("client_id not in redirect_uri")

        self.validate_json_schema(
            payload,
            "authorization_request",
            "Authen request object validation failed "
        )

    def get_url_consent(self, user):
        url = reverse("oidc_provider_consent")
        if (
                user.is_staff and
                'spid_cie_oidc.relying_party_test' in settings.INSTALLED_APPS
        ):
            try:
                url = reverse("oidc_provider_staff_testing")
            except Exception as e:  # pragma: no cover
                logger.error(f"testigng page url reverse failed: {e}")
        return url

    def get_login_form(self):
        return AuthLoginForm

    def get(self, request, *args, **kwargs):
        """
        The Authorization request of a RPs is validated and a login prompt is rendered to the user
        """
        req = request.GET.get("request", None)
        if not req:
            logger.error(
                f"Missing Authz request object in {dict(request.GET)} "
                f"error=invalid_request"
            )
            return HttpResponseBadRequest()
        # yes, again. We MUST.
        tc = None
        try:
            tc = self.validate_authz_request_object(req)
        except InvalidEntityConfiguration as e:
            # FIXME: to do test
            logger.error(f"Invalid Entity Configuration: {e}")
            return self.redirect_response_data(
                self.payload["redirect_uri"],
                error = "invalid_request",
                error_description =_("Failed to establish the Trust"),
                state = self.payload.get("state", "")
            )
        except AuthzRequestReplay as e:
            logger.error(
                "Replay on authz request detected for "
                f"{request.GET.get('client_id', 'unknow')}: {e}"
            )
            return self.redirect_response_data(
                self.payload["redirect_uri"],
                error = "invalid_request",
                error_description =_(
                    "An Unknown error raised during validation of "
                    f" authz request object: {e}"
                ),
                state = self.payload.get("state", "")

            )
        except Exception as e:
            logger.error(
                "Error during authz request validation for "
                f"{request.GET.get('client_id', 'unknown')}: {e}"
            )
            return self.redirect_response_data(
                self.payload["redirect_uri"],
                error="invalid_request",
                error_description=_("Authorization request not valid"),
                state = self.payload.get("state", "")

            )
        try:
            self.validate_authz(self.payload)
        except ValidationException:
            return self.redirect_response_data(
                self.payload["redirect_uri"],
                error="invalid_request",
                error_description=_("Authorization request validation error"),
                state = self.payload.get("state", "")
            )
        except InvalidRefreshRequestException as e:
            logger.warning(f"Invalid session: {e}")
            return HttpResponseForbidden()

        acr_value = AcrValues(self.payload["acr_values"][0])
        prompt = self.payload["prompt"]
        if request.user:
            if (
                    request.user.is_authenticated and
                    acr_value == AcrValues.l1 and
                    "login" not in prompt
            ):
                try:
                    session = self.check_session(request)
                    if session.acr != AcrValues.l1.value:
                        logout(request)
                        return self.get(request)
                    else:
                        url = self.get_url_consent(request.user)
                        return HttpResponseRedirect(url)
                except Exception:
                    logger.warning(
                        f"Failed SSO check session for {request.user}"
                    )
                    logout(request)
                    return self.get(request)

        # stores the authz request in a hidden field in the form
        form = self.get_login_form()()
        context = {
            "client_organization_name": tc.metadata.get(
                "client_name", self.payload["client_id"]
            ),
            "hidden_form": AuthzHiddenForm(dict(authz_request_object=req)),
            "form": form,
            "redirect_uri": self.payload["redirect_uri"],
            "obj_request": json.dumps(self.payload, indent=2),
            "acr_value": acr_value.name,
            "state": self.payload["state"]
        }
        return render(request, self.template, context)

    def post(self, request, *args, **kwargs):
        """
            When the User prompts his credentials
            TODO: REFACTOR this method doesn't support PAR!
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
                    "redirect_uri": self.payload["redirect_uri"],
                    "state": self.payload["state"]
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
        _provider_profile = getattr(
            settings,
            'OIDCFED_DEFAULT_PROVIDER_PROFILE',
            OIDCFED_DEFAULT_PROVIDER_PROFILE
        )
        default_acr = OIDCFED_PROVIDER_PROFILES_DEFAULT_ACR[_provider_profile]
        self.payload = self.string_to_list(self.payload, ["acr_values"])
        len_acr = len(self.payload.get("acr_values",[]))
        session = OidcSession.objects.create(
            user=user,
            user_uid=user.username,
            nonce=self.payload["nonce"],
            authz_request=self.payload,
            client_id=self.payload["client_id"],
            auth_code=auth_code,
            acr=(
                self.payload["acr_values"][len_acr - 1]
                if len_acr > 0
                else default_acr
            )
        )
        session.set_sid(request)
        url = self.get_url_consent(user)
        return HttpResponseRedirect(url)
