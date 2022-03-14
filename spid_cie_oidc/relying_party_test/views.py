import json
import logging

from django.http import HttpResponseForbidden
from django.views import View
from django.shortcuts import render
from spid_cie_oidc.provider.models import IssuedToken
from spid_cie_oidc.provider.views import OpBase
from spid_cie_oidc.relying_party_test.forms import TestingPageAttributesForm, TestingPageChecksForm, _


logger = logging.getLogger(__name__)


class StaffTestingPageView(OpBase, View):

    template = "op_user_staff_test.html"

    def get_testing_form(self):
        return TestingPageChecksForm

    def get(self, request):
        try:
            session = self.check_session(request)
        except Exception:
            logger.warning("Invalid session")
            return HttpResponseForbidden()

        session.user
        attributes = self.attributes_names_to_release(
            request, session
        )['filtered_user_claims']

        content = {
            "form_checks": self.get_testing_form()(),
            "form_attrs": TestingPageAttributesForm(),
            "attributes": json.dumps(attributes, indent=4),
            "session": session,
            "redirect_uri": session.authz_request.get('redirect_uri', "")
        }
        return render(request, self.template, content)

    def post(self, request):

        try:
            session = self.check_session(request)
        except Exception:
            logger.warning("Invalid session")
            return HttpResponseForbidden()

        form = self.get_testing_form()(request.POST)
        if not form.is_valid():
            return self.redirect_response_data(
                # TODO: this is not normative -> check AgID/IPZS
                session.authz_request['redirect_uri'],
                error="rejected_by_user",
                error_description=_(
                    "User rejected the release of attributes"
                )
            )

        issuer = self.get_issuer()
        iss_token_data = self.get_iss_token_data(session, issuer)

        IssuedToken.objects.create(**iss_token_data)
        self.payload = session.authz_request

        return self.redirect_response_data(
            self.payload["redirect_uri"],
            code=session.auth_code,
            state=session.authz_request["state"],
            iss=issuer.sub if issuer else ""
        )
