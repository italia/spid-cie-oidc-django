import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from spid_cie_oidc.authority.tests.settings import rp_conf
from spid_cie_oidc.entity.jwtse import create_jws
from spid_cie_oidc.provider.tests.settings import (
    op_conf, 
    op_conf_priv_jwk
)
from spid_cie_oidc.relying_party.models import (
    OidcAuthentication,
    OidcAuthenticationToken
)

RP_SUB = rp_conf["sub"]
RP_CLIENT_ID = rp_conf["metadata"]["openid_relying_party"]["client_id"]

class RpModelTest(TestCase):

    def setUp(self): 
        self.user = get_user_model().objects.create(
            username="test",
            first_name="test",
            last_name="test",
            email="test@test.it",
        )
        self.user.set_password("test")
        self.user.save()
        authz_request = OidcAuthentication.objects.create(
            client_id=rp_conf["metadata"]["openid_relying_party"]["client_id"],
            provider_configuration=op_conf["metadata"]["openid_provider"],
        )
        self.token = {
            "iss": op_conf["sub"],
            "sub": RP_SUB,
            "aud": [RP_CLIENT_ID],
            "client_id": RP_CLIENT_ID,
            "scope": "openid",
        }
        self.rt_jws = create_jws(self.token, op_conf_priv_jwk)
        self.authz_token = OidcAuthenticationToken.objects.create(
            user= self.user,
            authz_request = authz_request,
            code = "code",
            access_token = self.rt_jws,
            id_token = self.rt_jws,
        )

    def test_token_preview(self):
        result = OidcAuthenticationToken.token_preview(self.authz_token, self.rt_jws)
        self.assertTrue(json.loads(result)["iss"] == "http://op-test/oidc/op/")
        result = OidcAuthenticationToken.token_preview(self.authz_token, "")
        self.assertTrue(result == "--")
        result = OidcAuthenticationToken.token_preview(self.authz_token, "token")
        self.assertTrue(result == None)
        result = OidcAuthenticationToken.__str__(self.authz_token)
        self.assertTrue("code" in result)
        result = self.authz_token.access_token_preview
        self.assertTrue(json.loads(result)["iss"] == "http://op-test/oidc/op/")
        result = self.authz_token.id_token_preview
        self.assertTrue(json.loads(result)["iss"] == "http://op-test/oidc/op/")
