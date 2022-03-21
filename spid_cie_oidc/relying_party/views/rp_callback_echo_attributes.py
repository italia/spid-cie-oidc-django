import logging

from django.shortcuts import render
from django.views import View


logger = logging.getLogger(__name__)


class SpidCieOidcRpCallbackEchoAttributes(View):
    template = "echo_attributes.html"

    def get(self, request):
        data = {"oidc_rp_user_attrs": request.session.get("oidc_rp_user_attrs", {})}
        return render(request, self.template, data)
