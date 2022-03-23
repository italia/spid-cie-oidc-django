
from django.test import Client, TestCase
from django.urls import reverse
from spid_cie_oidc.authority.tests.settings import rp_conf


class NoConsentTest(TestCase):

    def setUp(self):
        pass

    def test_no_consent(self):
        client = Client()
        url = reverse("oidc_provider_not_consent")
        redirect_uri = rp_conf["metadata"]["openid_relying_party"]["redirect_uris"][0]
        res = client.get(url + "?redirect_uri=" + redirect_uri)
        self.assertTrue(res.status_code == 302)
        self.assertTrue("Authentication+request+rejected+by+user" in res.url)
