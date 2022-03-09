from copy import deepcopy

from django.test import TestCase
from spid_cie_oidc.authority.settings import FEDERATION_DEFAULT_POLICY
from spid_cie_oidc.entity.policy import apply_policy, diff2policy, gather_policies
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

