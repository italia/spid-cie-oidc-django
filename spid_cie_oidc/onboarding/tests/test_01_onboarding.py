from django.test import TestCase, Client, override_settings
from django.urls import reverse
import json

from spid_cie_oidc.authority.tests.settings import *
from spid_cie_oidc.entity.models import *
from spid_cie_oidc.onboarding.urls import *
from spid_cie_oidc.entity.jwks import serialize_rsa_key
from spid_cie_oidc.entity.jwks import new_rsa_key
from spid_cie_oidc.entity.tests.settings import *

from spid_cie_oidc.authority.models import *
from spid_cie_oidc.authority.tests.mocked_responses import *
from spid_cie_oidc.authority.tests.settings import *

from spid_cie_oidc.onboarding.tests.mocked_responses import *


from unittest.mock import patch


class OnboardingTest(TestCase):
    def setUp(self):

        self.rp_conf = FederationEntityConfiguration.objects.create(**rp_conf)

        self.data = {
            "organization_name": "",
            "url_entity": "",
            "authn_buttons_page_url": "",
            "type":"",
            "public_jwks": "",
        }

    @override_settings(HTTP_CLIENT_SYNC=True)
    @patch("requests.get", return_value=OnboardingRegistrationResponse())
    def test_onboarding_registration(self, mocked):
        url = reverse("oidc_onboarding_registration")
        client = Client()
        res = client.get(url, self.data)
        self.assertEqual(res.status_code, 200)
        res = client.post(url, self.data)
        self.assertFormError(
            res, "form", "organization_name", "Enter your organization name"
        )
        self.assertFormError(res, "form", "url_entity", "Enter your url of the entity")
        self.assertFormError(
            res, "form", "public_jwks", "Enter the public jwks of the entities"
        )
        self.assertEqual(res.status_code, 200)
        self.data["organization_name"] = "test name"
        self.data["url_entity"] = "http://rp-test/oidc/rp"
        self.data["type"] = "openid_relying_party"
        self.data["authn_buttons_page_url"] = "https://authnurl.com"
        self.data["public_jwks"] = {"key": "ciao"}
        res = client.post(url, self.data)
        self.assertContains(res, "Inserisci un JSON valido.")
        self.assertEqual(res.status_code, 200)
        jwk = serialize_rsa_key(new_rsa_key().pub_key)
        self.data["public_jwks"] = json.dumps(jwk)
        res = client.post(url, self.data)
        # self.assertEqual(res.status_code, 302)
        # res = client.get(res.url)
        # self.assertEqual(res.status_code, 200)
        # self.assertIn(self.data["organization_name"], res.content.decode())
        # self.assertIn("acquired", res.content.decode())

    def test_schema_authorization(self):
        c = Client()
        url = reverse("oidc_onboarding_schemas_Authorization")
        res = c.get(url)
        self.assertTrue(res.status_code == 200)
        self.assertIn("Schemas authorization endpoint", res.content.decode())

    def test_schema_introspection(self):
        c = Client()
        url = reverse("oidc_onboarding_schemas_introspection")
        res = c.get(url)
        self.assertTrue(res.status_code == 200)
        self.assertIn("Schemas introspection endpoint", res.content.decode())

    def test_schema_metadata(self):
        c = Client()
        url = reverse("oidc_onboarding_schemas_metadata")
        res = c.get(url)
        self.assertTrue(res.status_code == 200)
        self.assertIn("Schemas metadata Spid/Cie", res.content.decode())

    def test_schema_revocation(self):
        c = Client()
        url = reverse("oidc_onboarding_schemas_revocation")
        res = c.get(url)
        self.assertTrue(res.status_code == 200)
        self.assertIn("Schemas revocation endpoint", res.content.decode())

    def test_schema_token(self):
        c = Client()
        url = reverse("oidc_onboarding_schemas_token")
        res = c.get(url)
        self.assertTrue(res.status_code == 200)
        self.assertIn("Schemas token endpoint", res.content.decode())
        
    def test_schema_client_assertion(self):
        c = Client()
        url = reverse("oidc_onboarding_schemas_jwt_client_assertion")
        res = c.get(url)
        self.assertTrue(res.status_code == 200)
        self.assertIn("Schemas jwt", res.content.decode())
