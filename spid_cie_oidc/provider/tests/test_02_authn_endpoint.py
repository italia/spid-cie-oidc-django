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

# TODO: we need factory function to get fresh now
IAT = iat_now()
EXP = exp_from_now()

REQUEST_OBJECT_PAYLOAD = {
    'client_id': 'http://127.0.0.1:8000/oidc/rp/',
    'sub': 'http://rp-test/oidc/rp',
    'iss': 'http://rp-test/oidc/rp',
    'response_type': 'code',
    'scope': ['openid'],
    'code_challenge': 'qWJlMe0xdbXrKxTm72EpH659bUxAxw80',
    'code_challenge_method': 'S256',
    'nonce': 'MBzGqyf9QytD28eupyWhSqMj78WNqpc2',
    'prompt': 'consent login',
    'redirect_uri': 'http://rp-test/oidc/rp/callback1/',
    'acr_values': ['https://www.spid.gov.it/SpidL1', 'https://www.spid.gov.it/SpidL2'],
    'claims': {
        'id_token': {
            'family_name': {'essential': True},
            'email': {'essential': True}
        },
        'userinfo': {
            'given_name': None,
            'family_name': None
        }
    },
    'state': 'fyZiOL9Lf2CeKuNT2JzxiLRDink0uPcd',
    'iss': "https://op.spid.agid.gov.it/",
    'aud': ["https://rp.spid.agid.gov.it/auth"],
    'iat': IAT,
    'exp': EXP,
    'jti': "a72d5df0-2415-4c7c-a44f-3988b354040b"
}



class AuthnRequestTest(TestCase):

    def setUp(self):
        self.req = HttpRequest()
        breakpoint()
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
        res = client.post(res.url, {"username": "test", "password":"test"})
        self.assertTrue(res.status_code == 302)


