from django.test import TestCase, Client
from django.urls import reverse
import json

from spid_cie_oidc.entity.models import *
from spid_cie_oidc.onboarding.urls import *
from spid_cie_oidc.entity.jwks import serialize_rsa_key,new_rsa_key
from spid_cie_oidc.onboarding.tests.tools_settings import jwk_priv, jwk_pub, jwt
from spid_cie_oidc.onboarding.forms import OnboardingCreateTrustChain


from unittest.mock import patch

class ToolsTests(TestCase):

    def setUp(self):

        self.client = Client()
        self.data = {"organization_name" : "","url_entity" : "",
            "authn_buttons_page_url" : "","public_jwks" : ""
        }

    def test_create_jwk(self):
        url = reverse("oidc_onboarding_create_jwk")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(res.context['jwk'])

    # def test_convert_jwk_to_pem(self):
    #     url = reverse("oidc_onboarding_convert_jwk")
    #     res = self.client.get(url)
    #     self.assertEqual(res.status_code, 200)
    #     #check with jwk error
    #     res = self.client.post(url + '?type=private', {'kty': 'RSA'})
    #     self.assertEqual(res.status_code, 200)
    #     self.assertIn("alert-error", res.content.decode())
    #     #check with public jwk the function jwk priv to pem
    #     res = self.client.post(url + '?type=private', jwk_pub)
    #     self.assertEqual(res.status_code, 200)
    #     self.assertIn("alert-error", res.content.decode())
    #     #check with right jwk
    #     res = self.client.post(url + '?type=private', jwk_priv)
    #     self.assertEqual(res.status_code, 200)
    #     self.assertNotIn("alert-error", res.content.decode())
    #     #breakpoint()

    def test_decode_and_verify_jwt(self):
        url = reverse("oidc_onboarding_tools_decode_jwt")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        res = self.client.post(url, {"jwt":jwt})
        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(res.context['jwt'])
        self.assertIsNotNone(res.context['payload'])
        self.assertIsNotNone(res.context['head'])
        jwkError = {"jwkerror":"error"}
        jwk = json.dumps(jwkError)
        res = self.client.post(url, {"jwt":jwt, "jwk": jwk})
        self.assertEqual(res.status_code, 200)
        self.assertIn("alert-error", res.content.decode())
        jwk = json.dumps(jwk_priv)
        res = self.client.post(url, {"jwt":jwt, "jwk": jwk})
        self.assertEqual(res.status_code, 200)
        self.assertIn("alert-success", res.content.decode())

    def test_resolve_statement(self):
        url = reverse("oidc_onboarding_resolve_statement")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        res = self.client.get(url, {
            "sub":"http://127.0.0.1:8000/oidc/",
            "type": "openid_provider",
            "anchor": "http://127.0.0.1:8000/"
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn("alert-error", res.content.decode())
        self.assertIn(
            "Failed to resolve entity statement, Please check your inserted data", 
            res.content.decode())

        form_data= {
            "sub": "http://127.0.0.1:8000/oidc/op/",
            "type": "openid_provider",
            "anchor": "http://127.0.0.1:8000/",
        }
        res = self.client.get(url, form_data)
        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(res.context['resolved_statement'])

    def test_validating_trust_mark(self):
        url = reverse("oidc_onboarding_tools_validating_trustmark")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        # res = self.client.get(url, {
        #     "sub":"http://127.0.0.1:8000/oidc/",
        #     "type": "openid_provider",
        #     "anchor": "http://127.0.0.1:8000/"
        # })
        # self.assertEqual(res.status_code, 200)
        # self.assertIn("alert-error", res.content.decode())
        # self.assertIn(
        #     "Failed to resolve entity statement, Please check your inserted data", 
        #     res.content.decode())

        # form_data= {
        #     "sub": "http://127.0.0.1:8000/oidc/op/",
        #     "type": "openid_provider",
        #     "anchor": "http://127.0.0.1:8000/",
        # }
        # res = self.client.get(url, form_data)
        # self.assertEqual(res.status_code, 200)
        # self.assertIsNotNone(res.context['resolved_statement'])

    
