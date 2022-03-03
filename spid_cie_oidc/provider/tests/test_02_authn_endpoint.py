from copy import deepcopy

from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from spid_cie_oidc.authority.tests.settings import (
    RP_METADATA,
    rp_onboarding_data
)
from spid_cie_oidc.entity.jwtse import create_jws
from spid_cie_oidc.entity.models import (
    FederationEntityConfiguration,
    FetchedEntityStatement, 
    TrustChain
)
from spid_cie_oidc.entity.tests.settings import TA_SUB
from spid_cie_oidc.entity.utils import (
    datetime_from_timestamp, 
    exp_from_now,
    iat_now
)
from spid_cie_oidc.provider.tests.settings import op_conf

# TODO: we need factory function to get fresh now
IAT = iat_now()
EXP = exp_from_now()
RP_SUB = rp_onboarding_data["sub"]
REQUEST_OBJECT_PAYLOAD = {
    'client_id': RP_SUB,
    'sub': RP_SUB,
    'iss': RP_SUB,
    'response_type': 'code',
    'scope': ['openid'],
    'code_challenge': 'qWJlMe0xdbXrKxTm72EpH659bUxAxw80',
    'code_challenge_method': 'S256',
    'nonce': 'MBzGqyf9QytD28eupyWhSqMj78WNqpc2',
    'prompt': 'consent login',
    'redirect_uri': f'{RP_SUB}callback1/',
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
    'aud': ["https://op.spid.agid.gov.it/auth"],
    'iat': IAT,
    'exp': EXP,
    'jti': "a72d5df0-2415-4c7c-a44f-3988b354040b"
}


class AuthnRequestTest(TestCase):

    def setUp(self):
        self.req = HttpRequest()
        self.rp_jwk = RP_METADATA["openid_relying_party"]['jwks']['keys'][0]
        self.user = get_user_model().objects.create(
            username = "test",
            first_name ="test", 
            last_name= "test", 
            email="test@test.it")
        self.user.set_password("test")
        self.user.save()
        NOW = datetime_from_timestamp(iat_now())
        EXP = datetime_from_timestamp(exp_from_now(33))

        self.rp_conf = FederationEntityConfiguration.objects.create(**op_conf)

        self.ta_fes = FetchedEntityStatement.objects.create(
            sub = TA_SUB,
            iss = TA_SUB,
            exp = EXP,
            iat = NOW,
            )

        self.trust_chain = TrustChain.objects.create(
            sub = RP_SUB,
            type = "openid_relying_party",
            exp = EXP,
            metadata = RP_METADATA["openid_relying_party"],
            status = 'valid',
            trust_anchor = self.ta_fes,
            is_active = True
        )

    @override_settings(OIDCFED_TRUST_ANCHOR=TA_SUB)    
    def test_auth_request(self):
        jws=create_jws(REQUEST_OBJECT_PAYLOAD, self.rp_jwk)
        client = Client()
        url = reverse("oidc_provider_authnrequest")
        res = client.get(url, {"request": jws})
        self.assertTrue(res.status_code == 200)
        self.assertIn("username", res.content.decode())
        self.assertIn("password", res.content.decode())
        res = client.post(url, {"username": "test", "password":"test", "authz_request_object": jws})
        self.assertFalse("error" in res.content.decode())
        self.assertTrue(res.status_code == 302)

          
    @override_settings(OIDCFED_TRUST_ANCHOR=TA_SUB)
    def test_auth_request_wrong_login(self):
        REQUEST_OBJECT_PAYLOAD["nonce"]= '#'*32
        jws=create_jws(REQUEST_OBJECT_PAYLOAD, self.rp_jwk)
        client = Client()
        url = reverse("oidc_provider_authnrequest")
        res = client.get(url, {"request": jws})
        self.assertTrue(res.status_code == 200)
        self.assertIn("username", res.content.decode())
        self.assertIn("password", res.content.decode())
        res = client.post(url, {"username": "notest", "password":"test", "authz_request_object": jws})
        self.assertIn("error", res.content.decode())

    @override_settings(OIDCFED_TRUST_ANCHOR=TA_SUB)
    def test_auth_request_preexistent_authz(self):
        jws=create_jws(REQUEST_OBJECT_PAYLOAD, self.rp_jwk)
        client = Client()
        url = reverse("oidc_provider_authnrequest")
        res = client.get(url, {"request": jws})
        self.assertTrue(res.status_code == 200)
        self.assertIn("username", res.content.decode())
        self.assertIn("password", res.content.decode())
        res = client.post(url, {"username": "test", "password":"test", "authz_request_object": jws})
        res = client.get(url, {"request": jws})
        self.assertTrue(res.status_code == 302)
        self.assertIn("error=invalid_request", res.url)


    @override_settings(OIDCFED_TRUST_ANCHOR=TA_SUB)
    def test_auth_request_trust_chain_no_active(self):
        self.trust_chain.is_active = False
        self.trust_chain.save()
        jws=create_jws(REQUEST_OBJECT_PAYLOAD, self.rp_jwk)
        client = Client()
        url = reverse("oidc_provider_authnrequest")
        res = client.get(url, {"request": jws})
        self.assertTrue(res.status_code == 302)
        self.assertIn("error=access_denied", res.url)

    @override_settings(OIDCFED_TRUST_ANCHOR=TA_SUB)
    def test_auth_request_invalid_jwk(self):
        jws=create_jws(REQUEST_OBJECT_PAYLOAD, self.rp_jwk)
        self.trust_chain.metadata['jwks']['keys'][0]["kid"] = "31ALfVXx9dcAMMHCVvh42qLTlanBL_r6BTnD5uMDzFT"
        self.trust_chain.save()
        client = Client()
        url = reverse("oidc_provider_authnrequest")
        res = client.get(url, {"request": jws})
        self.assertTrue(res.status_code == 302)
        self.assertIn("error=unauthorized_client", res.url)

    @override_settings(OIDCFED_TRUST_ANCHOR=TA_SUB)
    def test_auth_request_no_correct_payload(self):
        NO_CORRECT_OBJECT_PAYLOAD = deepcopy(REQUEST_OBJECT_PAYLOAD)
        NO_CORRECT_OBJECT_PAYLOAD["response_type"] = "test"
        jws=create_jws(NO_CORRECT_OBJECT_PAYLOAD, self.rp_jwk)
        client = Client()
        url = reverse("oidc_provider_authnrequest")
        res = client.get(url, {"request": jws})
        self.assertTrue(res.status_code == 302)
        self.assertIn("error=invalid_request", res.url)
