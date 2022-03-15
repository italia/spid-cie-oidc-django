import logging
import urllib.parse

from django.contrib.auth import logout
from django.http import (
    HttpResponseForbidden,
    HttpResponseRedirect,
)
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views import View
from spid_cie_oidc.entity.models import (
    TrustChain
)
from spid_cie_oidc.provider.forms import ConsentPageForm
from spid_cie_oidc.provider.models import IssuedToken

from . import OpBase

logger = logging.getLogger(__name__)


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
                state = self.payload.get("state", "")
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
