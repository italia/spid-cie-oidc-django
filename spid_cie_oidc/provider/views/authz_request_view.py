import hashlib
import logging
import urllib.parse
import uuid

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.forms import ValidationError
from django.forms.utils import ErrorList
from django.http import (
    HttpResponseForbidden,
    HttpResponseRedirect,
)
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views import View
from spid_cie_oidc.entity.exceptions import InvalidEntityConfiguration
from spid_cie_oidc.provider.forms import AuthLoginForm, AuthzHiddenForm
from spid_cie_oidc.provider.models import OidcSession

from spid_cie_oidc.provider.exceptions import AuthzRequestReplay, ValidationException
from spid_cie_oidc.provider.settings import OIDCFED_DEFAULT_PROVIDER_PROFILE, OIDCFED_PROVIDER_PROFILES_DEFAULT_ACR

from . import OpBase
logger = logging.getLogger(__name__)


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
                if ' ' in payload[i]:
                    payload[i] = payload[i].split(' ')
                else:
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
                "Error during trust build for "
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
        _provider_profile = getattr(
            settings,
            'OIDCFED_DEFAULT_PROVIDER_PROFILE',
            OIDCFED_DEFAULT_PROVIDER_PROFILE
        )
        default_acr = OIDCFED_PROVIDER_PROFILES_DEFAULT_ACR[_provider_profile]
        session = OidcSession.objects.create(
            user=user,
            user_uid=user.username,
            nonce=self.payload["nonce"],
            authz_request=self.payload,
            client_id=self.payload["client_id"],
            auth_code=auth_code,
            acr=(
                self.payload["acr_values"][-1]
                if len(self.payload.get("acr_values",[])) > 0
                else default_acr
            )
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
