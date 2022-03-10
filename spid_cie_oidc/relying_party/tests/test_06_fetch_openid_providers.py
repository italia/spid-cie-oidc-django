

from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase, override_settings
from spid_cie_oidc.authority.tests.settings import RP_METADATA_JWK1
from spid_cie_oidc.entity.models import FetchedEntityStatement, TrustChain
from spid_cie_oidc.entity.tests.settings import TA_SUB
from spid_cie_oidc.entity.utils import (
    datetime_from_timestamp, 
    exp_from_now,
    iat_now
)
from spid_cie_oidc.provider.tests.settings import op_conf

EXP = datetime_from_timestamp(exp_from_now(33))
NOW = datetime_from_timestamp(iat_now())
ta_fes = FetchedEntityStatement.objects.create(
    sub=TA_SUB,
    iss=TA_SUB,
    exp=EXP,
    iat=NOW,
)
TC = TrustChain.objects.create(
    sub=op_conf["sub"],
    type="openid_relying_party",
    exp=EXP,
    metadata=op_conf["metadata"]["openid_provider"],
    status="valid",
    trust_anchor=ta_fes,
    is_active=True,
)
class FetchProviderTest(TestCase):

    def setUp(self):

        self.ta_fes = FetchedEntityStatement.objects.create(
            sub=TA_SUB,
            iss=TA_SUB,
            exp=datetime_from_timestamp(exp_from_now(33)),
            iat=datetime_from_timestamp(iat_now()),
        )

    def exec(self, cmd_name:str, *args, **kwargs):
        call_command(
            cmd_name,
            *args,
            **kwargs,
        )
    
    @patch("spid_cie_oidc.entity.trust_chain_operations.get_or_create_trust_chain", return_value = TC)
    @override_settings(OIDCFED_IDENTITY_PROVIDERS = {"http://127.0.0.1:8000/oidc/op/" :"http://testserver/"})
    def test_fetch_provider(self, mocked):
        out = self.exec('fetch_openid_providers', '--start')


