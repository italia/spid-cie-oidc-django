
import json
import logging
from django.http import HttpResponse, HttpResponseRedirect

from django.test import Client, RequestFactory
from django.urls import reverse
from spid_cie_oidc.onboarding.tests.token_response_settings import TOKEN_RESPONSE
from spid_cie_oidc.provider.tests.settings import op_conf
from spid_cie_oidc.entity.jwks import create_jwk
from spid_cie_oidc.entity.jwtse import create_jws
logger = logging.getLogger(__name__)

class TokenEndPointResponse():
    def __init__(self):
        self.status_code = 200

    @property
    def content(self):
        data = {}
        jwk = {}
        breakpoint()
        jws = create_jws(data, jwk)
        return json.dump(jws).encode()
# def __init__(self):
#         self.status_code = 200
#         self.client = Client()

#     @property
#     def content(self):
#         breakpoint()

#         return json.dumps(TOKEN_RESPONSE).encode()