from copy import deepcopy

from django.test import TestCase
from spid_cie_oidc.authority.settings import FEDERATION_DEFAULT_POLICY
from spid_cie_oidc.entity.policy import (
    apply_policy, 
    diff2policy,
    gather_policies,
    PolicyError
)
from spid_cie_oidc.entity.tests.rp_metadata_settings import RP_METADATA
from spid_cie_oidc.authority.tests.settings import rp_onboarding_data


class PolicyTest(TestCase):
    def setUp(self):
        pass

    def test_gather_polices(self):
        combined_policy = gather_policies([{}], "openid_relying_party")
        self.assertTrue(combined_policy == {})

    def test_gather_polices_rp(self):
        combined_policy = gather_policies([{},rp_onboarding_data], "openid_relying_party")
        self.assertTrue(combined_policy == {'scope': {'value': ['openid']}})

    def test_apply_policy(self):
        fa_policy = {}
        fa_policy["scope"] = FEDERATION_DEFAULT_POLICY["openid_relying_party"][
            "scope"
        ]
        fa_policy["contacts"] = {"add": "ciao@email.it"}
        combined_policy = apply_policy(deepcopy(RP_METADATA), fa_policy)
        combined_contacts = combined_policy["contacts"]
        self.assertTrue("ciao@email.it" in combined_contacts)
        self.assertTrue("ops@rp.example.it" in combined_contacts)
        
    def test_apply_policy_one_of(self):
        fa_policy = {}
        fa_policy["logo_uri"] = {"one_of": ["logo1", "logo2"]}
        with self.assertRaises(PolicyError):
            apply_policy(deepcopy(RP_METADATA), fa_policy)

    def test_apply_policy_subset_of(self):
        fa_policy = {}
        fa_policy["scope"] = {"subset_of": ["openid", "offline_access"]}
        combined_contacts = apply_policy(deepcopy(RP_METADATA), fa_policy)
        self.assertTrue('profile' not in combined_contacts["scope"])

    def test_apply_policy_superset_of(self):
        fa_policy = {}
        fa_policy["scope"] = {"superset_of": ["openid"]}
        RP_METADATA_LOCAL = deepcopy(RP_METADATA)
        RP_METADATA_LOCAL["scope"] = ["offline_access"]
        with self.assertRaises(PolicyError):
            apply_policy(deepcopy(RP_METADATA_LOCAL), fa_policy)

    def test_apply_policy_difference_value(self):
        fa_policy = {}
        fa_policy["client_id"] = {"value":  "https://rp.example.it/spid"}
        RP_METADATA_LOCAL = deepcopy(RP_METADATA)
        RP_METADATA_LOCAL.pop("client_id")
        combined_contacts = apply_policy(deepcopy(RP_METADATA_LOCAL), fa_policy)
        self.assertTrue(combined_contacts["client_id"])

    def test_apply_policy_difference_add(self):
        fa_policy = {}
        fa_policy["contacts"] = {"add": "ciao@email.it"}
        RP_METADATA_LOCAL = deepcopy(RP_METADATA)
        RP_METADATA_LOCAL.pop("contacts")
        combined_contacts = apply_policy(deepcopy(RP_METADATA_LOCAL), fa_policy)
        self.assertTrue(combined_contacts["contacts"])
        self.assertTrue("ciao@email.it" in combined_contacts["contacts"])

    def test_apply_policy_add(self):
        fa_policy = {}
        fa_policy["contacts"] = {"add": "ciao@email.it"}
        combined_contacts = apply_policy(deepcopy(RP_METADATA), fa_policy)
        self.assertTrue("ciao@email.it" in combined_contacts["contacts"])
        self.assertTrue("ops@rp.example.it" in combined_contacts["contacts"])


    def test_diff_two_policy(self):
        fa_policy_old = {}
        fa_policy_old["scope"] = FEDERATION_DEFAULT_POLICY["openid_relying_party"][
            "scope"
        ]
        fa_policy_new = deepcopy(fa_policy_old)
        fa_policy_new["contacts"] = {"add": "test@email.it"}
        result = diff2policy(fa_policy_new, fa_policy_old)
        diff = {
            "contacts": {
                "add": {
                    "add": "test@email.it"
                    }
                }
            }
        self.assertTrue(result == diff)
