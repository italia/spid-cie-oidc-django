from copy import deepcopy
import json
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from spid_cie_oidc.accounts.models import User
from spid_cie_oidc.entity.models import FederationEntityConfiguration
from spid_cie_oidc.entity.utils import get_jwks

from spid_cie_oidc.relying_party.models import OidcAuthentication
from spid_cie_oidc.authority.tests.settings import rp_conf
from spid_cie_oidc.provider.tests.settings import op_conf
from spid_cie_oidc.provider.tests.authn_request_settings import AUTHN_REQUEST_SPID

from spid_cie_oidc.relying_party.tests.mocked_response import (
    MockedTokenEndPointNoCorrectIdTokenResponse,
    MockedTokenEndPointNoCorrectResponse, 
    MockedTokenEndPointResponse, 
    MockedUserInfoResponse
)


STATE = "fyZiOL9Lf2CeKuNT2JzxiLRDink0uPcd"
CODE = "usDwMnEzJPpG5oaV8x3j&"


class RpCallBack(TestCase):
    def setUp(self):
        self.rp_jwk = {
            'kty': 'RSA', 
            'kid': '19xSsWuFOo5bFBUECA5G3V5GEhC0s7X8TTCEykdzsmo', 
            'e': 'AQAB', 
            'n': 'vfzFzFAv4e1IPfH6XMeB_L3f9sRZuaOtRsAs7s6ujGv6PwVMPsdELqd2NzrmKrLih3ZysJ6RoRe87rGZUZu2GbDtZhupCPb-1MuxB810svua9PwCrQK2wADM8q26colAiAOGSt912LUPC6MOYus44xd7TUDtQcsm-3VXWu4DA19NQXOaUh2TRal6GKXr7D8teod0fo736oHTObWoDZ0KdAGlwxI6IbQKpipgTD6lZ3l9L6WSmdLI9T-TyyNV9fW6rNqhnbySCEGkCM-Up6C2GQqLTq76kQNSMGasXrd3qH07KnTLBZsFy4JV4L-ws3zgaB4PLBOdfYAYe-xSp9-H_Q', 'd': 'MYc9FXduFCrko2l6yEcmhvoE8fLcJT4bRQ-CZzswW-EmWtmJt_AAwVzcv6c2K7l4vrHNUmf0NRfYJC3ed1ztiyMJsI3TckfZxSXY39za6HIZQnaUSAAmHkXXKAjMS2Gmlg69KrW4picFZhY7AOSrbuBHP6uGbpmEbxd3D3hvBqiU6cn_TAwbIhsJniTuSYYbvHd8z93QCKBfp_nDMltz6WG8YUXFiqtzRKv62Y4K2J_zjyd7-JKiWEBh5FUNuqZ2txEV3-q6bwoh3lSGA1qZtVgU61CwHqGQK3uxfEGPV68O48NVJNEe4YgNE806IfREgprTe3osGHd2S96s-t8oYQ', 
            'p': '9pwMs9MCfes5vYzXb8n1BqAL3LGdPp48jg7iKD4mZ6oLpeCbwNqtB7zN24OqrOnP2nREL2ugkSU2bBrsMy1hZ6k2DnN7cZkNgv4CZ_lO35Bc9CF9j1sCTxUnXQknympL8HVZoG2TdxUL0P09TgiBYz8SVH-uxFnlCuVZBLx35Lk', 
            'q': 'xTjFHi0QGPYSXGgbUN5cl9LOw7K2ifULDbEPiYSnbzd_oVneA-q6BmanMM5CLrj8qKJPy2Cuz3do-ZZPG_SN5AU_x23K9Vga3honcomo7G0cYKi9wGPBKzAMCRNRFHp3f3BAcp6HUJRn02Q_F_xDmXeC8JiPeATSBIDCXv41I2U'
        }
        data = deepcopy(AUTHN_REQUEST_SPID)
        self.rp_config = deepcopy(rp_conf)
        authz_entry = dict(
            client_id=self.rp_config["metadata"]["openid_relying_party"]["client_id"],
            provider_id=op_conf["sub"],
            data=json.dumps(data),
            state=STATE,
            provider_configuration=op_conf["metadata"]["openid_provider"],
        )
        OidcAuthentication.objects.create(**authz_entry)
        self.rp_config["sub"] = self.rp_config["metadata"]["openid_relying_party"]["client_id"]
        FederationEntityConfiguration.objects.create(**self.rp_config)
        rp_conf_saved = FederationEntityConfiguration.objects.all().first()
        get_jwks(rp_conf_saved.metadata['openid_relying_party'])[0]["kid"] = rp_conf_saved.jwks_core[0]["kid"]
        rp_conf_saved.save()
        self.op_conf = FederationEntityConfiguration.objects.create(**op_conf)

    @override_settings(HTTP_CLIENT_SYNC=True)
    @patch("requests.post", return_value=MockedTokenEndPointResponse())
    @patch("requests.get", return_value=MockedUserInfoResponse())
    def test_rp_callback(self, mocked, mocked_2):
        client = Client()
        url = reverse("spid_cie_rp_callback")
        res = client.get(url, {"state": STATE, "code": CODE})
        user = get_user_model().objects.first()
        self.assertTrue(
            user.attributes['fiscal_number'] == "sdfsfs908df09s8df90s8fd0"
        )

    @override_settings(HTTP_CLIENT_SYNC=True)
    @patch("requests.post", return_value=MockedTokenEndPointResponse())
    @patch("requests.get", return_value=MockedUserInfoResponse())
    def test_rp_callback_mixups_attacks(self, mocked, mocked_2):
        client = Client()
        url = reverse("spid_cie_rp_callback")
        res = client.get(url, {"state": STATE, "code": CODE, "iss": "WRONG"})
        self.assertTrue(res.status_code == 400)

    @override_settings(HTTP_CLIENT_SYNC=True)
    @patch("spid_cie_oidc.relying_party.views.rp_callback.process_user_attributes", return_value=None)
    @patch("requests.post", return_value=MockedTokenEndPointResponse())
    @patch("requests.get", return_value=MockedUserInfoResponse())
    def test_rp_callback_no_rp_attr_map(self, mocked, mocked_2, mocked_3):
        client = Client()
        url = reverse("spid_cie_rp_callback")
        res = client.get(url, {"state": STATE, "code": CODE})
        self.assertTrue(res.status_code == 403)

    @override_settings(HTTP_CLIENT_SYNC=True)
    @patch("spid_cie_oidc.relying_party.views.rp_callback.process_user_attributes", return_value=None)
    @patch("requests.post", return_value=MockedTokenEndPointResponse())
    @patch("requests.get", return_value=MockedUserInfoResponse())
    def test_rp_callback_incorret_request(self, mocked, mocked_2, mocked_3):
        client = Client()
        url = reverse("spid_cie_rp_callback")
        res = client.get(url, {})
        self.assertTrue("error" in res.json())

    @override_settings(HTTP_CLIENT_SYNC=True)
    @patch("spid_cie_oidc.relying_party.views.rp_callback.process_user_attributes", return_value=None)
    @patch("requests.post", return_value=MockedTokenEndPointResponse())
    @patch("spid_cie_oidc.relying_party.views.rp_callback.SpidCieOidcRpCallbackView.get_userinfo", return_value=None)
    def test_rp_callback_no_userinfo(self, mocked, mocked_2, mocked_3):
        client = Client()
        url = reverse("spid_cie_rp_callback")
        res = client.get(url, {"state": STATE, "code": CODE})
        self.assertTrue(res.status_code == 400)
        
    @override_settings(HTTP_CLIENT_SYNC=True)
    @patch("spid_cie_oidc.relying_party.views.rp_callback.process_user_attributes", return_value=None)
    @patch("spid_cie_oidc.relying_party.views.rp_callback.SpidCieOidcRpCallbackView.access_token_request", return_value=None)
    def test_rp_callback_no_token_response(self, mocked, mocked_2):
        client = Client()
        url = reverse("spid_cie_rp_callback")
        res = client.get(url, {"state": STATE, "code": CODE})
        self.assertTrue(res.status_code == 400)
        self.assertTrue("invalid token response" in res.content.decode())

    @override_settings(HTTP_CLIENT_SYNC=True)
    @patch("requests.post", return_value=MockedTokenEndPointResponse())
    @patch("requests.get", return_value=MockedUserInfoResponse())
    def test_rp_callback_no_rp_conf(self, mocked, mocked_2):
        FederationEntityConfiguration.objects.filter(
            sub = self.rp_config["sub"]
        ).delete()
        client = Client()
        url = reverse("spid_cie_rp_callback")
        res = client.get(url, {"state": STATE, "code": CODE})
        self.assertTrue("Relying party not found" in res.content.decode())

    @override_settings(HTTP_CLIENT_SYNC=True)
    @patch("requests.post", return_value=MockedTokenEndPointResponse())
    @patch("requests.get", return_value=MockedUserInfoResponse())
    def test_rp_callback_no_authz(self, mocked, mocked_2):
        OidcAuthentication.objects.all().delete()
        client = Client()
        url = reverse("spid_cie_rp_callback")
        res = client.get(url, {"state": STATE, "code": CODE})
        self.assertTrue("Authentication not found" in res.content.decode())

    @override_settings(HTTP_CLIENT_SYNC=True)
    @patch("requests.post", return_value=MockedTokenEndPointResponse())
    @patch("requests.get", return_value=MockedUserInfoResponse())
    def test_rp_callback_reunification(self, mocked, mocked_2):
        user = User.objects.create(username = "username", attributes = {"fiscal_number" : "sdfsfs908df09s8df90s8fd0"}),
        client = Client()
        url = reverse("spid_cie_rp_callback")
        res = client.get(url, {"state": STATE, "code": CODE})
        user = get_user_model().objects.first()
        self.assertTrue(
            user.attributes['fiscal_number'] == "sdfsfs908df09s8df90s8fd0"
        )

    @override_settings(HTTP_CLIENT_SYNC=True)
    @patch("requests.post", return_value=MockedTokenEndPointNoCorrectResponse())
    @patch("requests.get", return_value=MockedUserInfoResponse())
    def test_rp_callback_no_correct_token_response(self, mocked, mocked1):
        client = Client()
        url = reverse("spid_cie_rp_callback")
        res = client.get(url, {"state": STATE, "code": CODE})
        self.assertTrue(res.status_code == 400)
        self.assertTrue("invalid_request" in res.content.decode())

    @override_settings(HTTP_CLIENT_SYNC=True)
    @patch("requests.post", return_value=MockedTokenEndPointNoCorrectIdTokenResponse())
    @patch("requests.get", return_value=MockedUserInfoResponse())
    def test_rp_callback_no_correct_id_token_response(self, mocked, mocked1):
        client = Client()
        url = reverse("spid_cie_rp_callback")
        res = client.get(url, {"state": STATE, "code": CODE})
        self.assertTrue(res.status_code == 403)
        self.assertTrue("invalid_token" in res.content.decode())
