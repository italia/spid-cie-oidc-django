from copy import deepcopy
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from spid_cie_oidc.authority.tests.settings import RP_METADATA, RP_METADATA_JWK1, rp_onboarding_data
from django.utils import timezone

from spid_cie_oidc.entity.jwtse import create_jws, unpad_jwt_payload, verify_jws
from spid_cie_oidc.entity.models import (
    FederationEntityConfiguration,
    FetchedEntityStatement,
    TrustChain,
)
from spid_cie_oidc.entity.tests.settings import TA_SUB
from spid_cie_oidc.entity.utils import datetime_from_timestamp, exp_from_now, iat_now
from spid_cie_oidc.entity.utils import get_jwks
from spid_cie_oidc.provider.models import IssuedToken, OidcSession
from spid_cie_oidc.provider.tests.settings import op_conf, op_conf_priv_jwk
from spid_cie_oidc.relying_party.utils import random_string

RP_SUB = rp_onboarding_data["sub"]

class AuthnRequestTest(TestCase):
    def setUp(self):

        self.REQUEST_OBJECT_PAYLOAD = {
            "client_id": RP_SUB,
            "sub": RP_SUB,
            "iss": RP_SUB,
            "response_type": "code",
            "scope": ["openid"],
            "code_challenge": "qWJlMe0xdbXrKxTm72EpH659bUxAxw80",
            "code_challenge_method": "S256",
            "nonce": random_string(),
            "prompt": "consent login",
            "redirect_uri": f"{RP_SUB}callback/",
            "acr_values": ["https://www.spid.gov.it/SpidL1", "https://www.spid.gov.it/SpidL2"],
            "claims": {
                "id_token": {"family_name": {"essential": True}, "email": {"essential": True}},
                "userinfo": {"given_name": None, "family_name": None, "email": None},
            },
            "state": random_string(),
            "aud": ["https://op.spid.agid.gov.it/auth"],
            "iat": iat_now(),
            "exp": exp_from_now(),
            "jti": "a72d5df0-2415-4c7c-a44f-3988b354040b",
        }

        self.user = get_user_model().objects.create(
            username="test",
            first_name="test",
            last_name="test",
            email="test@test.it",
            is_staff= False,
            attributes={
                "family_name": "rossi",
                "username": "unique_value",
                "fiscal_number": "a7s6da87d6a87sd6as78d",
                "email": "test@test.it",
            },
        )
        self.user.set_password("test")
        self.user.save()
        self.op_conf = FederationEntityConfiguration.objects.create(**op_conf)
        self.ta_fes = FetchedEntityStatement.objects.create(
            sub=TA_SUB,
            iss=TA_SUB,
            exp=datetime_from_timestamp(exp_from_now(33)),
            iat=datetime_from_timestamp(iat_now()),
        )
        self.trust_chain = TrustChain.objects.create(
            sub=RP_SUB,
            exp=datetime_from_timestamp(exp_from_now(33)),
            jwks = [],
            metadata=RP_METADATA,
            status="valid",
            trust_anchor=self.ta_fes,
            is_active=True,
        )

    @override_settings(OIDCFED_DEFAULT_TRUST_ANCHOR=TA_SUB)
    def test_auth_request_unknown_error(self):
        jws = create_jws(self.REQUEST_OBJECT_PAYLOAD, RP_METADATA_JWK1)
        client = Client()
        TrustChain.objects.all().delete()
        url = reverse("oidc_provider_authnrequest")
        res = client.get(url, {"request": jws})
        self.assertTrue(res.status_code == 302)
        self.assertTrue("error=invalid_request" in res.url)

    @override_settings(OIDCFED_DEFAULT_TRUST_ANCHOR=TA_SUB)
    @override_settings(OIDCFED_DEFAULT_PROVIDER_PROFILE="cie")
    def test_auth_request_id_token_claim(self):
        jws = create_jws(self.REQUEST_OBJECT_PAYLOAD, RP_METADATA_JWK1)
        client = Client()
        url = reverse("oidc_provider_authnrequest")
        res = client.get(url, {"request": jws})
        self.assertTrue(res.status_code == 200)
        self.assertIn("username", res.content.decode())
        self.assertIn("password", res.content.decode())
        res = client.post(
            url, {"username": "test", "password": "test", "authz_request_object": jws}
        )
        self.assertFalse("error" in res.content.decode())
        self.assertTrue(res.status_code == 302)
        consent_page_url = res.url
        res = client.get(consent_page_url)
        self.assertTrue("agree" in res.content.decode())
        self.assertFalse("error" in res.content.decode())
        res = client.post(consent_page_url, {"agree": True})
        issued_token = IssuedToken.objects.all().first()
        verify_jws(issued_token.id_token, op_conf_priv_jwk)
        id_token = unpad_jwt_payload(issued_token.id_token)
        self.assertEqual(id_token.get("family_name"), "rossi")
        self.assertEqual(id_token.get("email"), "test@test.it")


    @override_settings(OIDCFED_DEFAULT_TRUST_ANCHOR=TA_SUB)
    def test_auth_no_request(self):
        client = Client()
        url = reverse("oidc_provider_authnrequest")
        res = client.get(url, {})
        self.assertTrue(res.status_code == 400)

    @override_settings(OIDCFED_DEFAULT_TRUST_ANCHOR=TA_SUB)
    def test_auth_request_ok(self):
        jws = create_jws(self.REQUEST_OBJECT_PAYLOAD, RP_METADATA_JWK1)
        client = Client()
        url = reverse("oidc_provider_authnrequest")
        res = client.get(url, {"request": jws})
        self.assertTrue(res.status_code == 200)
        self.assertIn("username", res.content.decode())
        self.assertIn("password", res.content.decode())
        res = client.post(
            url, {"username": "test", "password": "test", "authz_request_object": jws}
        )
        self.assertFalse("error" in res.content.decode())
        self.assertTrue(res.status_code == 302)
        consent_page_url = res.url
        res = client.get(consent_page_url)
        self.assertTrue("agree" in res.content.decode())
        self.assertFalse("error" in res.content.decode())
        res = client.post(consent_page_url, {"agree": True})
        self.assertTrue(res.status_code == 302)
        self.assertTrue("code" in res.url)

    @override_settings(OIDCFED_DEFAULT_TRUST_ANCHOR=TA_SUB)
    def test_auth_request_user_rejected_consent(self):
        jws = create_jws(self.REQUEST_OBJECT_PAYLOAD, RP_METADATA_JWK1)
        client = Client()
        url = reverse("oidc_provider_authnrequest")
        res = client.get(url, {"request": jws})
        self.assertTrue(res.status_code == 200)
        self.assertIn("username", res.content.decode())
        self.assertIn("password", res.content.decode())
        res = client.post(
            url, {"username": "test", "password": "test", "authz_request_object": jws}
        )
        self.assertFalse("error" in res.content.decode())
        self.assertTrue(res.status_code == 302)
        consent_page_url = res.url
        res = client.get(consent_page_url)
        self.assertTrue("agree" in res.content.decode())
        self.assertFalse("error" in res.content.decode())
        res = client.post(consent_page_url, {"agree": False})
        self.assertTrue(res.status_code == 302)
        # TODO: this is not normative
        self.assertTrue("error=rejected_by_user" in res.url)

    @override_settings(OIDCFED_DEFAULT_TRUST_ANCHOR=TA_SUB)
    def test_auth_request_no_session_in_post_consent(self):
        jws = create_jws(self.REQUEST_OBJECT_PAYLOAD, RP_METADATA_JWK1)
        client = Client()
        url = reverse("oidc_provider_authnrequest")
        res = client.get(url, {"request": jws})
        self.assertTrue(res.status_code == 200)
        self.assertIn("username", res.content.decode())
        self.assertIn("password", res.content.decode())
        res = client.post(
            url, {"username": "test", "password": "test", "authz_request_object": jws}
        )
        self.assertFalse("error" in res.content.decode())
        self.assertTrue(res.status_code == 302)
        consent_page_url = res.url
        res = client.get(consent_page_url)
        self.assertTrue("agree" in res.content.decode())
        self.assertFalse("error" in res.content.decode())
        OidcSession.objects.all().delete()
        res = client.post(consent_page_url, {"agree": True})
        self.assertTrue(res.status_code == 403)

    @override_settings(OIDCFED_DEFAULT_TRUST_ANCHOR=TA_SUB)
    def test_auth_request_no_session_in_get_consent(self):
        jws = create_jws(self.REQUEST_OBJECT_PAYLOAD, RP_METADATA_JWK1)
        client = Client()
        url = reverse("oidc_provider_authnrequest")
        res = client.get(url, {"request": jws})
        self.assertTrue(res.status_code == 200)
        self.assertIn("username", res.content.decode())
        self.assertIn("password", res.content.decode())
        res = client.post(
            url,
            {
                "username": "test", 
                "password": "test", 
                "authz_request_object": jws
            }
        )
        self.assertFalse("error" in res.content.decode())
        self.assertTrue(res.status_code == 302)
        consent_page_url = res.url
        OidcSession.objects.all().delete()
        res = client.get(consent_page_url)
        self.assertTrue(res.status_code == 403)

    @override_settings(OIDCFED_DEFAULT_TRUST_ANCHOR=TA_SUB)
    def test_auth_request_auth_code_already_used(self):
        jws = create_jws(self.REQUEST_OBJECT_PAYLOAD, RP_METADATA_JWK1)
        client = Client()
        url = reverse("oidc_provider_authnrequest")
        res = client.get(url, {"request": jws})
        self.assertTrue(res.status_code == 200)
        self.assertIn("username", res.content.decode())
        self.assertIn("password", res.content.decode())
        res = client.post(
            url, {"username": "test", "password": "test", "authz_request_object": jws}
        )
        self.assertFalse("error" in res.content.decode())
        self.assertTrue(res.status_code == 302)
        session = OidcSession.objects.all().first()
        IssuedToken.objects.create(session=session, expires=timezone.localtime())
        consent_page_url = res.url
        res = client.get(consent_page_url)
        self.assertTrue(res.status_code == 403)

    @override_settings(OIDCFED_DEFAULT_TRUST_ANCHOR=TA_SUB)
    def test_auth_request_wrong_login(self):
        jws = create_jws(self.REQUEST_OBJECT_PAYLOAD, RP_METADATA_JWK1)
        client = Client()
        url = reverse("oidc_provider_authnrequest")
        res = client.get(url, {"request": jws})
        self.assertTrue(res.status_code == 200)
        self.assertIn("username", res.content.decode())
        self.assertIn("password", res.content.decode())
        res = client.post(
            url, {"username": "notest", "password": "test", "authz_request_object": jws}
        )
        self.assertIn("error", res.content.decode())

    @override_settings(OIDCFED_DEFAULT_TRUST_ANCHOR=TA_SUB)
    def test_auth_request_preexistent_authz(self):
        jws = create_jws(self.REQUEST_OBJECT_PAYLOAD, RP_METADATA_JWK1)
        client = Client()
        url = reverse("oidc_provider_authnrequest")
        res = client.get(url, {"request": jws})
        self.assertTrue(res.status_code == 200)
        self.assertIn("username", res.content.decode())
        self.assertIn("password", res.content.decode())
        res = client.post(
            url, {"username": "test", "password": "test", "authz_request_object": jws}
        )
        res = client.get(url, {"request": jws})
        self.assertTrue(res.status_code == 302)
        self.assertIn("error=invalid_request", res.url)
        self.assertIn("state", res.url)

    @override_settings(OIDCFED_DEFAULT_TRUST_ANCHOR=TA_SUB)
    def test_auth_request_trust_chain_no_active(self):
        self.trust_chain.is_active = False
        self.trust_chain.save()
        jws = create_jws(self.REQUEST_OBJECT_PAYLOAD, RP_METADATA_JWK1)
        client = Client()
        url = reverse("oidc_provider_authnrequest")
        res = client.get(url, {"request": jws})
        self.assertTrue(res.status_code == 302)
        self.assertIn("error=invalid_request", res.url)
        self.assertIn("state", res.url)

    @override_settings(OIDCFED_DEFAULT_TRUST_ANCHOR=TA_SUB)
    def test_auth_request_invalid_jwk(self):
        jws = create_jws(self.REQUEST_OBJECT_PAYLOAD, RP_METADATA_JWK1)
        get_jwks(self.trust_chain.metadata['openid_relying_party'])[0][
            "kid"
        ] = "31ALfVXx9dcAMMHCVvh42qLTlanBL_r6BTnD5uMDzFT"
        self.trust_chain.save()
        client = Client()
        url = reverse("oidc_provider_authnrequest")
        res = client.get(url, {"request": jws})
        self.assertTrue(res.status_code == 302)
        self.assertIn("error=invalid_request", res.url)
        self.assertIn("state", res.url)
        get_jwks(self.trust_chain.metadata['openid_relying_party'])[0][
            "kid"
        ] = RP_METADATA_JWK1['kid']
        self.trust_chain.save()

    @override_settings(OIDCFED_DEFAULT_TRUST_ANCHOR=TA_SUB)
    def test_auth_request_no_correct_payload(self):
        NO_CORRECT_OBJECT_PAYLOAD = deepcopy(self.REQUEST_OBJECT_PAYLOAD)
        NO_CORRECT_OBJECT_PAYLOAD["response_type"] = "test"
        jws = create_jws(NO_CORRECT_OBJECT_PAYLOAD, RP_METADATA_JWK1)
        client = Client()
        url = reverse("oidc_provider_authnrequest")
        res = client.get(url, {"request": jws})
        self.assertTrue(res.status_code == 302)
        self.assertIn("error", res.url)
        self.assertIn("state", res.url)

    @override_settings(OIDCFED_DEFAULT_TRUST_ANCHOR=TA_SUB)
    def test_auth_request_invalid_session(self):
        client = Client()
        url = reverse("oidc_provider_consent")
        res = client.get(url)
        self.assertTrue(res.status_code == 403)
        res = client.post(url)
        self.assertTrue(res.status_code == 403)

    @override_settings(OIDCFED_DEFAULT_TRUST_ANCHOR=TA_SUB)
    def test_auth_request_no_correct_refresh_request(self):
        local_payload = deepcopy(self.REQUEST_OBJECT_PAYLOAD)
        local_payload["scope"] = "openid offline_access"
        local_payload["prompt"] = "login"
        jws = create_jws(local_payload, RP_METADATA_JWK1)
        client = Client()
        url = reverse("oidc_provider_authnrequest")
        res = client.get(url, {"request": jws})
        self.assertTrue(res.status_code == 403)
    
    @override_settings(OIDCFED_DEFAULT_TRUST_ANCHOR=TA_SUB)
    def test_auth_request_user_staff(self):
        self.user.is_staff = True
        self.user.save()
        jws = create_jws(self.REQUEST_OBJECT_PAYLOAD, RP_METADATA_JWK1)
        client = Client()
        url = reverse("oidc_provider_authnrequest")
        res = client.post(
            url, {"username": "test", "password": "test", "authz_request_object": jws}
        )
        self.assertTrue(res.status_code == 302)
        self.assertTrue("/oidc/op/rp-test/landing/" == res.url)

    @override_settings(OIDCFED_DEFAULT_TRUST_ANCHOR=TA_SUB)
    def test_auth_request_no_correct_authz_request(self):
        self.user.is_staff = True
        self.user.save()
        create_jws(self.REQUEST_OBJECT_PAYLOAD, RP_METADATA_JWK1)
        client = Client()
        url = reverse("oidc_provider_authnrequest")
        res = client.post(
            url, {"username": "test", "password": "test", "authz_request_object": {}}
        )
        self.assertTrue(res.status_code == 403)

