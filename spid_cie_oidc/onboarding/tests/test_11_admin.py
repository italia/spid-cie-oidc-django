
from django.test import TestCase
from spid_cie_oidc.authority.models import FederationDescendant, FederationDescendantContact

from spid_cie_oidc.onboarding.admin import OnBoardingRegistrationAdmin
from spid_cie_oidc.onboarding.models import OnBoardingRegistration

from spid_cie_oidc.authority.tests.settings import RP_METADATA_JWK1_pub, rp_conf
class AdminTest(TestCase):

    def setUp(self):
        self.onb_regist = OnBoardingRegistration.objects.create(
            organization_name = "RP test",
            url_entity = rp_conf["sub"],
            public_jwks = RP_METADATA_JWK1_pub,
            type = "openid_relying_party",
            contact = "ops@rp.example.it"
        )
        print(self.onb_regist)

    def test_make_published(self):
        queryset = [self.onb_regist]
        OnBoardingRegistrationAdmin.enable_as_descendant(None, request = {}, queryset = queryset)
        self.assertTrue(len(FederationDescendantContact.objects.all()) == 1)
        self.assertTrue(len(FederationDescendant.objects.all()) == 1)