
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from spid_cie_oidc.authority.tests.settings import rp_conf
from spid_cie_oidc.provider.models import OidcSession


class UserAccessHistoryTest(TestCase):

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
            user_uid="uid",
            nonce="",
            authz_request={
                "scope": "openid", 
                "nonce": "123", 
                "acr_values" : ["https://www.spid.gov.it/SpidL2"],            
                "redirect_uri" : rp_conf["metadata"]["openid_relying_party"]["redirect_uris"][0],
                "state" : "state",
            },
            client_id="",
            auth_code="auth_code",
        )
        OidcSession.objects.create(
            user=self.user,
            user_uid="uid",
            nonce="1234",
            authz_request={
                "scope": "openid", 
                "nonce": "1234", 
                "acr_values" : ["https://www.spid.gov.it/SpidL2"],            
                "redirect_uri" : rp_conf["metadata"]["openid_relying_party"]["redirect_uris"][0],
                "state" : "state",
            },
            client_id="",
            auth_code="code",
        )


    def test_user_access_history(self):
        client = Client()
        client.login(username="test", password="test")
        session = client.session
        session.update({"oidc": {"auth_code": "code"}, "user_uid" : "uid"})
        session.save()
        url = reverse("oidc_provider_access_history")
        res = client.get(url)
        self.assertTrue(res.status_code == 200)
        self.assertTrue("auth_code=auth_code" in res.content.decode())

    def test_user_access_history_revoke(self):
        client = Client()
        client.login(username="test", password="test")
        session = client.session
        session.update({"oidc": {"auth_code": "code"}, "user_uid" : "uid"})
        session.save()
        url = reverse("oidc_provider_revoke_session")
        res = client.get(url, {"auth_code": "auth_code"})
        self.assertTrue(res.status_code == 302)
        url_history = reverse("oidc_provider_access_history")
        self.assertTrue(url_history in res.url)
