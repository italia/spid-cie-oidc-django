from django.test import Client, TestCase
from django.urls import reverse
from spid_cie_oidc.entity.models import FetchedEntityStatement, TrustChain
from spid_cie_oidc.entity.tests.settings import TA_SUB
from spid_cie_oidc.entity.utils import (
    datetime_from_timestamp, 
    exp_from_now,
    iat_now
)
from spid_cie_oidc.provider.tests.settings import op_conf


class RpLandingTest(TestCase):

    def setUp(self) -> None:
        NOW = datetime_from_timestamp(iat_now())
        EXP = datetime_from_timestamp(exp_from_now(33))
        self.ta_fes = FetchedEntityStatement.objects.create(
            sub=TA_SUB,
            iss=TA_SUB,
            exp=EXP,
            iat=NOW,
        )

        self.trust_chain = TrustChain.objects.create(
            sub=op_conf["sub"],
            exp=EXP,
            jwks = [],
            metadata=op_conf["metadata"],
            status="valid",
            trust_anchor=self.ta_fes,
            is_active=True,
        )

    def test_rp_landing(self):
        client = Client()
        url = reverse("spid_cie_rp_landing")
        res = client.get(url)
        self.assertTrue(res.status_code == 200)
        
