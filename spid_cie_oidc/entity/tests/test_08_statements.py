
from unittest.mock import patch
from django.test import  TestCase, override_settings
from spid_cie_oidc.authority.models import FederationDescendant, FederationEntityAssignedProfile, FederationEntityProfile

from spid_cie_oidc.authority.tests.mocked_responses import EntityResponseNoIntermediate
from spid_cie_oidc.entity.models import FederationEntityConfiguration

from spid_cie_oidc.entity.tests.settings import ta_conf_data
from spid_cie_oidc.authority.tests.settings import (
    rp_conf,
    RP_PROFILE,
    rp_onboarding_data
)
from spid_cie_oidc.entity.statements import TrustMark

class StatementTest(TestCase):

    def setUp(self):
        self.ta_conf = FederationEntityConfiguration.objects.create(**ta_conf_data)
        self.rp_conf = FederationEntityConfiguration.objects.create(**rp_conf)

        self.rp_profile = FederationEntityProfile.objects.create(**RP_PROFILE)
        self.rp = FederationDescendant.objects.create(**rp_onboarding_data)

        self.rp_assigned_profile = FederationEntityAssignedProfile.objects.create(
            descendant=self.rp, profile=self.rp_profile, issuer=self.ta_conf
        )
        self.trust_mark = self.rp_assigned_profile.trust_mark_as_jws


    @override_settings(HTTP_CLIENT_SYNC=True)
    @patch("requests.get", return_value=EntityResponseNoIntermediate())
    def test_validate_by_its_issuer(self, mocked):
        self.tm = TrustMark(self.trust_mark)
        TrustMark.validate_by_its_issuer(self.tm)
        self.assertTrue(self.tm.is_valid)

    
    