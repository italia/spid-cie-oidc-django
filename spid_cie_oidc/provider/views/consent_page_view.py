import logging
from django.core.paginator import Paginator
import urllib.parse

from djagger.decorators import schema
from django.contrib.auth import logout
from django.http import (
    HttpResponseForbidden,
    HttpResponseRedirect,
)
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _
from django.views import View
from spid_cie_oidc.entity.models import (
    TrustChain
)
from spid_cie_oidc.provider.forms import ConsentPageForm
from spid_cie_oidc.provider.models import IssuedToken, OidcSession
from spid_cie_oidc.provider.settings import OIDCFED_PROVIDER_HISTORY_PER_PAGE

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
            metadata__openid_relying_party__isnull=False,
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
            "user_claims": sorted(set(i18n_user_claims),),
            "redirect_uri": session.authz_request["redirect_uri"],
            "state": session.authz_request["state"]
        }
        return render(request, self.template, context)

    def post(self, request, *args, **kwargs):
        try:
            session = self.check_session(request)
        except Exception as e:
            logger.warning(f"Invalid session: {e}")
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
    redirect_uri = request.GET.get("redirect_uri")
    state = request.GET.get("state", "")
    logout(request)
    kwargs = dict(
        error = "invalid_request",
        error_description = _(
            "Authentication request rejected by user"
        ),
        state = state
    )
    url = f'{redirect_uri}?{urllib.parse.urlencode(kwargs)}'
    return HttpResponseRedirect(url)


class UserAccessHistoryView(OpBase, View):

    def get(self, request, *args, **kwargs):
        try:
            session = self.check_session(request)
        except Exception: # pragma: no cover
            logger.warning("Invalid session on Access History page")
            return HttpResponseForbidden()
        user_access_history = OidcSession.objects.filter(
            user_uid=session.user_uid,
        ).exclude(auth_code=session.auth_code)
        paginator = Paginator(
            user_access_history,
            OIDCFED_PROVIDER_HISTORY_PER_PAGE
        )
        page = request.GET.get("page", 1)
        history = paginator.get_page(page)
        context = {
            "history": history,
            "user": request.user
        }
        return render(request, "op_user_history.html", context)


@schema(
    methods = [],
    djagger_exclude=True
)
class RevokeSessionView(OpBase, View):

    def get(self, request, *args, **kwargs):
        try:
            self.check_session(request)
        except Exception: # pragma: no cover
            logger.warning("Invalid session on revoke page")
            return HttpResponseForbidden()

        if request.GET.get("auth_code"):
            auth_code = request.GET["auth_code"]
            session_to_revoke = OidcSession.objects.filter(
                auth_code=auth_code,
                user=request.user
            ).first()
            session_to_revoke.revoke(destroy_session=False)
        return redirect("oidc_provider_access_history")
