

from copy import deepcopy
import json
from unittest.mock import patch
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from spid_cie_oidc.entity.models import FederationEntityConfiguration

from spid_cie_oidc.relying_party.models import OidcAuthentication
from spid_cie_oidc.authority.tests.settings import rp_conf
from spid_cie_oidc.provider.tests.settings import op_conf
from spid_cie_oidc.onboarding.tests.authn_request_settings import AUTHN_REQUEST_SPID
from spid_cie_oidc.relying_party.tests.mocked_response import TokenEndPointResponse

STATE = "fyZiOL9Lf2CeKuNT2JzxiLRDink0uPcd"
CODE = "usDwMnEzJPpG5oaV8x3j&"

class RpCallBack(TestCase):

    def setUp(self):
        data = deepcopy(AUTHN_REQUEST_SPID)
        authz_entry = dict(
            client_id=rp_conf["metadata"]["openid_relying_party"]["client_id"],
            provider=op_conf["sub"],
            provider_id=op_conf["sub"],
            data = json.dumps(data),
            state= STATE,
            provider_configuration=json.dumps(op_conf["metadata"]["openid_provider"])
        )
        self.rp_config = deepcopy(rp_conf)
        self.rp_config["sub"] = rp_conf["metadata"]["openid_relying_party"]["client_id"]
        OidcAuthentication.objects.create(**authz_entry)
        self.rp_conf = FederationEntityConfiguration.objects.create(**self.rp_config)
        self.op_conf = FederationEntityConfiguration.objects.create(**op_conf)

    @override_settings(HTTP_CLIENT_SYNC=True)
    @patch("requests.post", return_value=TokenEndPointResponse())
    def test_rp_callback(self, mocked):
        client = Client()
        url = reverse("spid_cie_rp_callback")
        res = client.get(url, {"state": STATE, "code": CODE})