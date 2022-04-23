from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from spid_cie_oidc.entity.models import *
from spid_cie_oidc.entity.jwtse import verify_jws

from . import get_admin_change_view_url
from .settings import *


class EntityConfigurationTest(TestCase):
    def setUp(self):
        self.ta_conf = FederationEntityConfiguration.objects.create(**ta_conf_data)
        self.admin_user = get_user_model().objects.create_superuser(
            username="superuser", password="secret", email="admin@example.com"
        )

    def test_entity_configuration_admin(self):
        c = Client()
        c.login(username="superuser", password="secret")

        # run test
        response = c.get(get_admin_change_view_url(self.ta_conf))
        self.assertEqual(response.status_code, 200)

    def test_entity_configuration(self):
        self.assertTrue(
            isinstance(
                FederationEntityConfiguration.get_active_conf(),
                FederationEntityConfiguration,
            )
        )
        self.assertTrue(isinstance(self.ta_conf, FederationEntityConfiguration))
        self.assertFalse(self.ta_conf.is_leaf)

        for i in (
            "public_jwks",
            "pems_as_json",
            "kids",
            "type",
            "entity_configuration_as_jws",
        ):
            attr = getattr(self.ta_conf, i)
            self.assertTrue(attr)

        md = self.ta_conf.entity_configuration_as_dict["metadata"]["federation_entity"]
        for i in ("federation_fetch_endpoint",):
            self.assertTrue(md.get(i))

        # dulcis in fundo -> test the .well-knwon/openid-federation
        wk_url = reverse("entity_configuration")
        c = Client()
        res = c.get(wk_url)
        verify_jws(res.content.decode(), self.ta_conf.jwks_fed[0])
