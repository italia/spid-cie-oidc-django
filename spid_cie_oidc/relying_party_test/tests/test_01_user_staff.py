from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from spid_cie_oidc.authority.tests.settings import rp_conf
from spid_cie_oidc.entity.models import FederationEntityConfiguration
from spid_cie_oidc.provider.models import OidcSession
from spid_cie_oidc.provider.tests.settings import op_conf


class RPTetstTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create(
            username="test",
            first_name="test",
            last_name="test",
            email="test@test.it",
            is_staff = True
        )
        self.user.set_password("test")
        self.user.save()
        OidcSession.objects.create(
            user=self.user,
            user_uid="",
            nonce="",
            authz_request={
                "scope": "openid", 
                "nonce": "123", 
                "acr_values" : ["https://www.spid.gov.it/SpidL2"],            
                "redirect_uri" : rp_conf["metadata"]["openid_relying_party"]["redirect_uris"][0],
                "state" : "state",
            },
            client_id="",
            auth_code="code",
        )
        self.op_conf = FederationEntityConfiguration.objects.create(**op_conf)


    def test_user_staff_get(self):
        c = Client()
        c.login(username="test", password="test")
        session = c.session
        session.update({"oidc": {"auth_code": "code"}})
        session.save()
        url = reverse("oidc_provider_staff_testing")
        res = c.get(url)
        self.assertTrue("test page" in res.content.decode())

    def test_user_staff_post(self):
        c = Client()
        c.login(username="test", password="test")
        session = c.session
        session.update({"oidc": {"auth_code": "code"}})
        session.save()
        url = reverse("oidc_provider_staff_testing")
        res = c.post(url)
        self.assertTrue(res.status_code == 302)
        self.assertTrue("callback" in res.url)

    def test_user_staff_get_no_session(self):
        c = Client()
        c.login(username="test", password="test")
        url = reverse("oidc_provider_staff_testing")
        res = c.get(url)
        self.assertTrue(res.status_code == 403)

    def test_user_staff_post_no_session(self):
        c = Client()
        c.login(username="test", password="test")
        url = reverse("oidc_provider_staff_testing")
        res = c.post(url)
        self.assertTrue(res.status_code == 403)
