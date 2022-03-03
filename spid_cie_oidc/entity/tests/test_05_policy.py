from django.test import TestCase
from spid_cie_oidc.entity.policy import gather_policies


class PolicyTest(TestCase):

    def setUp(self):
        pass

    def test_gather_polices(self):
        combined_policy = gather_policies([{}], "openid_relying_party")
        self.assertTrue(combined_policy == {})

