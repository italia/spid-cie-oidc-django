from django.test import TestCase

from spid_cie_oidc.entity.models import *

from .settings import *

ta_conf_data = dict(
    sub=TA_SUB,
    metadata=FA_METADATA,
    constraints=FA_CONSTRAINTS,
    is_active=1,
    trust_mark_issuers=TM_ISSUERS,
)


class TrustChainTest(TestCase):
    def setUp(self):
        self.ta_conf = FederationEntityConfiguration.objects.create(**ta_conf_data)

    # def test_crypt_and_decrypt(self):
