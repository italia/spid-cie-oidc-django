from copy import deepcopy
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from spid_cie_oidc.authority.tests.settings import rp_conf
from spid_cie_oidc.entity.models import FederationEntityConfiguration
from spid_cie_oidc.provider.tests.settings import op_conf
from spid_cie_oidc.relying_party.models import (
    OidcAuthentication,
    OidcAuthenticationToken
)
from spid_cie_oidc.relying_party.tests.mocked_response import MockedLogout


class RpIntiatedLogoutTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create(
            username="test",
            first_name="test",
            last_name="test",
            email="test@test.it",
        )
        self.user.set_password("test")
        self.user.save()
        authz_request = OidcAuthentication.objects.create(
            client_id=rp_conf["metadata"]["openid_relying_party"]["client_id"],
            provider_configuration=op_conf["metadata"]["openid_provider"],
        )
        self.authz_token = OidcAuthenticationToken.objects.create(
            user= self.user,
            authz_request = authz_request,
        )
        FederationEntityConfiguration.objects.create(**rp_conf)
        self.admin_user = get_user_model().objects.create_superuser(
            username="superuser", password="secret", email="admin@example.com"
        )

    
    @patch("requests.post", return_value=MockedLogout())
    def test_rpinitaited_logout(self, mokced):
        c = Client()
        c.login(username="test", password="test")
        url = reverse("spid_cie_rpinitiated_logout")
        res = c.get(url)
        self.assertTrue(res.status_code == 302)
        self.assertTrue(res.url == "/oidc/rp/landing")

    def test_rpinitaited_logout_no_revocation_endpoint(self):
        OidcAuthentication.objects.all().delete()
        op_conf_local = deepcopy(op_conf["metadata"]["openid_provider"])
        op_conf_local.pop("revocation_endpoint")
        authz_request = OidcAuthentication.objects.create(
            client_id=rp_conf["metadata"]["openid_relying_party"]["client_id"],
            provider_configuration=op_conf_local,
        )
        self.authz_token = OidcAuthenticationToken.objects.create(
            user= self.user,
            authz_request = authz_request,
        )
        c = Client()
        c.login(username="test", password="test")
        url = reverse("spid_cie_rpinitiated_logout")
        res = c.get(url)
        self.assertTrue(res.status_code == 302)
        self.assertTrue(res.url == "/oidc/rp/landing")

    def test_rpinitaited_logout_no_auth_token(self):
        OidcAuthenticationToken.objects.all().delete()
        c = Client()
        c.login(username="test", password="test")
        url = reverse("spid_cie_rpinitiated_logout")
        res = c.get(url)
        self.assertTrue(res.status_code == 302)
        self.assertTrue(res.url == "/oidc/rp/landing")
