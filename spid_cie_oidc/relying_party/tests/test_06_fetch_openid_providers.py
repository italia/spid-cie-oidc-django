

from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase, override_settings
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


def create_tc():
    ta_fes = FetchedEntityStatement.objects.create(
        sub=TA_SUB,
        iss=TA_SUB,
        exp=EXP,
        iat=NOW
    )
    return TrustChain.objects.create(
        sub=op_conf["sub"],
        exp=EXP,
        jwks = [],
        metadata=op_conf["metadata"],
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

    @override_settings(OIDCFED_IDENTITY_PROVIDERS = {"spid": {"http://127.0.0.1:8000/oidc/op/" :"http://testserver/"}, "cie":{}})
    def test_fetch_provider(self):
        self.patcher = patch(
            "spid_cie_oidc.entity.trust_chain_operations.get_or_create_trust_chain", 
            return_value = create_tc()
        )
        self.patcher.start()
        self.exec('fetch_openid_providers', '--start')
        self.patcher.stop()

