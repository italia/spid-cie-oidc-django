import logging

from django.shortcuts import render
from django.views import View


logger = logging.getLogger(__name__)


class SpidCieOidcRpCallbackEchoAttributes(View):
    template = "echo_attributes.html"

    def get(self, request):
        data = {"oidc_rp_user_attrs": request.session.get("oidc_rp_user_attrs", {}),
                "at_expiration": request.session.get("at_expiration"),
                "at_jti": request.session.get("at_jti"),
                "rt_expiration": request.session.get("rt_expiration"),
                "rt_jti": request.session.get("rt_jti")}
        return render(request, self.template, data)
