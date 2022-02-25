from django.test import Client, TestCase
from django.urls import reverse

from spid_cie_oidc.relying_party.models import OidcAuthenticationToken
from spid_cie_oidc.relying_party.utils import html_json_preview


class OidcRpTest(TestCase):
    # TODO: re enable
    def _test_stupid_logout(self):
        # a stupid logout that MUST fail
        url = f'{reverse("spid_cie_rpinitiated_logout")}'
        req = Client()
        res = req.get(url)
        self.assertTrue(res.status_code == 302)
        # end stupid logout test

    # TODO: re enable
    def _test_session(self):
        url = f'{reverse("spid_cie_rp_begin")}?issuer_id=op_test'
        req = Client()
        res = req.get(url)
        self.assertTrue(res.status_code == 302)

        authz_url = f'{reverse("op_test:spid_oidc_op_authz")}?{res.url.split("?")[1]}'
        res = req.get(authz_url)
        self.assertTrue(res.status_code == 302)
        self.assertIn("code=", res.url)

        url = f'{reverse("spid_cie_rp_callback")}?{res.url.split("?")[1]}'
        res = req.get(url)
        self.assertTrue(res.status_code == 302)

        url = f'{reverse("spid_cie_rp_echo_attributes")}'
        res = req.get(url)
        self.assertIn("sando", res.content.decode())

        # test models
        tokens = OidcAuthenticationToken.objects.first()

        tokens.access_token_preview
        tokens.id_token_preview

        # and now logout
        url = f'{reverse("spid_cie_rpinitiated_logout")}'
        res = req.get(url)
        self.assertTrue(res.status_code == 302)

    # TODO: re enable
    def _test_html_json_preview(self):
        html_json_preview('{"a" : 34, "b" : 78}')
