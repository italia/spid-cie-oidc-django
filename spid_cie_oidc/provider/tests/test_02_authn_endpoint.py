from django.http import HttpRequest
from django.test import Client, TestCase
from django.urls import reverse
from spid_cie_oidc.authority.tests.settings import *
from spid_cie_oidc.entity.jwtse import create_jws
from spid_cie_oidc.entity.models import FetchedEntityStatement, TrustChain
from spid_cie_oidc.entity.tests.settings import *
from spid_cie_oidc.entity.utils import (datetime_from_timestamp, exp_from_now,
                                        iat_now)
from spid_cie_oidc.provider.tests.authn_endpoint_settings import *

NOW = datetime_from_timestamp(iat_now())
EXP = datetime_from_timestamp(exp_from_now(33))

class AuthnRequestTest(TestCase):

    def setUp(self):
        self.req = HttpRequest()


    def test_auth_request(self):

        fes = FetchedEntityStatement.objects.create(
            sub = "http://rp-test/oidc/rp",
            iss = "http://rp-test/oidc/rp",
            exp = EXP,
            iat = NOW,
            )
        
        TrustChain.objects.create(
            sub = 'http://rp-test/oidc/rp',
            type = "openid_relying_party",
            exp = EXP,
            metadata = METADATA,
            status = 'valid',
            trust_anchor = fes,
            is_active = True
            )

        jws=create_jws(PAYLOAD,JWK)
        client = Client()
        url = reverse("oidc_provider_authnrequest")
        res = client.get(url, {"request": jws})
        self.assertTrue(res.status_code == 200)
        self.assertIn("username", res.content.decode())
        self.assertIn("password", res.content.decode())


