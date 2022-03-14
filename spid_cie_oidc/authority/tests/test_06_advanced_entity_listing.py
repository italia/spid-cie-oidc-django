from copy import deepcopy

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from spid_cie_oidc.authority.models import FederationDescendant
from spid_cie_oidc.authority.tests.settings import rp_onboarding_data
from spid_cie_oidc.entity.models import FederationEntityConfiguration
from spid_cie_oidc.entity.tests.settings import ta_conf_data


class AdvanceEntityListing(TestCase):

    def setUp(self):
        FederationDescendant.objects.create(**rp_onboarding_data)
        rp_onboarding_data_local = deepcopy(rp_onboarding_data)
        rp_onboarding_data_local["sub"] = "http://rp-test.it/oidc/rplocal/"
        FederationDescendant.objects.create(**rp_onboarding_data_local)
        FederationEntityConfiguration.objects.create(**ta_conf_data)

    @override_settings(MAX_ENTRIES_PAGE=1)
    def test_advanced_entity_listing_1(self):
        url = reverse("oidcfed_advanced_entity_listing")
        data = {"page":2}
        res = Client().get(url, data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json().get("iss"), "http://testserver/")
        self.assertEqual(len(res.json().get("entities")), 2)
        self.assertEqual(res.json().get("page"), 2)
        url_prev_page = reverse("oidcfed_advanced_entity_listing")
        self.assertEqual(res.json().get("prev_page_path"), f"{url_prev_page}?page=1")

    @override_settings(MAX_ENTRIES_PAGE=1)
    def test_advanced_entity_listing_no_page(self):
        url = reverse("oidcfed_advanced_entity_listing")
        res = Client().get(url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json().get("iss"), "http://testserver/")
        self.assertEqual(len(res.json().get("entities")), 2)
        self.assertEqual(res.json().get("page"), 1)
        url_next_page = reverse("oidcfed_advanced_entity_listing")
        self.assertEqual(res.json().get("next_page_path"), f"{url_next_page}?page=2")

    def test_advanced_entity_listing_missing_trust_anchor(self):
        FederationEntityConfiguration.objects.all().delete()
        c = Client()
        url = reverse("oidcfed_advanced_entity_listing")
        res = c.get(url)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json().get("error"), "Missing trust anchor")
