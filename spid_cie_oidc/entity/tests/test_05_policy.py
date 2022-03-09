from copy import deepcopy

from django.test import TestCase
from spid_cie_oidc.authority.settings import FEDERATION_DEFAULT_POLICY
from spid_cie_oidc.entity.policy import (
    PolicyError, 
    apply_policy,
    combine_claim_policy, diff2policy,
    gather_policies
)
from spid_cie_oidc.entity.tests.rp_metadata_settings import RP_METADATA


class PolicyTest(TestCase):
    def setUp(self):
        pass

    def test_gather_polices(self):
        combined_policy = gather_policies([{}], "openid_relying_party")
        self.assertTrue(combined_policy == {})

    def test_apply_policy(self):
        fa_policy = {}
        fa_policy["scopes"] = FEDERATION_DEFAULT_POLICY["openid_relying_party"][
            "scopes"
        ]
        fa_policy["contacts"] = {"add": "ciao@email.it"}
        combined_policy = apply_policy(deepcopy(RP_METADATA), fa_policy)
        combined_contacts = combined_policy["contacts"]
        self.assertTrue("ciao@email.it" in combined_contacts)
        self.assertTrue("ops@rp.example.it" in combined_contacts)
        
    def test_diff_two_policy(self):
        fa_policy_old = {}
        fa_policy_old["scopes"] = FEDERATION_DEFAULT_POLICY["openid_relying_party"][
            "scopes"
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

    def test_combine_claim_policy(self):
        superior = {}
        child = {}
        combined = combine_claim_policy(superior, child)
        self.assertEquals(combined, {})
        superior = {"value" : "val"}
        child = {"essential": False}
        combined = combine_claim_policy(superior, child)
        self.assertEquals(combined, {"value": "val", "essential": False})
        child = {"essential": "ess", "add" : "added"}
        with self.assertRaises(PolicyError):
            combine_claim_policy(superior, child)
        child = {"value": "valChild", "add" : "added"}
        with self.assertRaises(PolicyError):
            combine_claim_policy(superior, child)
        child = {"value": "val", "add" : "added"}
        combined = combine_claim_policy(superior, child)
        self.assertEquals(combined, superior)
        child = {"add" : "added"}
        with self.assertRaises(PolicyError):
            combine_claim_policy(superior, child)
        child = {}
        combined = combine_claim_policy(superior, child)
        self.assertEquals(combined, superior)
        superior = {"essential": True}
        child = {"essential": False}
        with self.assertRaises(PolicyError):
            combine_claim_policy(superior, child)
        child = {"essential": True, "one_of" : True, "subset_of": []}
        with self.assertRaises(PolicyError):
            combine_claim_policy(superior, child)
        superior = { "superset_of": []}
        child = { "subset_of": []}
        combined = combine_claim_policy(superior, child)
        self.assertEquals(combined, {'superset_of': [], 'subset_of': []})
        child = { "subset_of": [], "default" : ""}
        combined = combine_claim_policy(superior, child)
        self.assertEquals(combined, {'subset_of': [], 'superset_of': [], 'default': ''})
        child = { "default" : ""}
        combined = combine_claim_policy(superior, child)
        self.assertEquals(combined, {'superset_of': [], 'default': ''})
        superior = { "subset_of": []}
        combined = combine_claim_policy(superior, child)
        self.assertEquals(combined, {'subset_of': [], 'default': ''})

