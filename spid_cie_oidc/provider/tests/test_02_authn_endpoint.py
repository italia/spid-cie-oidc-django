from django.http import HttpRequest
from django.test import Client, TestCase
from django.urls import reverse
from spid_cie_oidc.accounts.models import User
from spid_cie_oidc.authority.tests.settings import (
    RP_METADATA,
    rp_onboarding_data
)
from spid_cie_oidc.entity.jwtse import create_jws
from spid_cie_oidc.entity.models import FetchedEntityStatement, TrustChain
from spid_cie_oidc.entity.utils import (
    datetime_from_timestamp, 
    exp_from_now,
    iat_now
)

from .authn_endpoint_settings import REQUEST_OBJECT_PAYLOAD


class AuthnRequestTest(TestCase):

    def setUp(self):
        self.req = HttpRequest()
        self.rp_jwk = RP_METADATA["openid_relying_party"]['jwks']['keys'][0]
        User.objects.create(first_name ="test", last_name= "test", email="test@test.it")

    def test_auth_request(self):

        NOW = datetime_from_timestamp(iat_now())
        EXP = datetime_from_timestamp(exp_from_now(33))

        fes = FetchedEntityStatement.objects.create(
            sub = rp_onboarding_data["sub"],
            iss = rp_onboarding_data["sub"],
            exp = EXP,
            iat = NOW,
            )

        TrustChain.objects.create(
            sub = rp_onboarding_data["sub"],
            type = "openid_relying_party",
            exp = EXP,
            metadata = RP_METADATA["openid_relying_party"],
            status = 'valid',
            trust_anchor = fes,
            is_active = True
        )
        breakpoint()
        jws=create_jws(REQUEST_OBJECT_PAYLOAD, self.rp_jwk)
        client = Client()
        url = reverse("oidc_provider_authnrequest")
        res = client.get(url, {"request": jws})
        self.assertTrue(res.status_code == 200)
        self.assertIn("username", res.content.decode())
        self.assertIn("password", res.content.decode())


