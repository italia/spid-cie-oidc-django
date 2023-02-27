

from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase, override_settings
from spid_cie_oidc.authority.tests.settings import (
    RP_CONF_AS_JSON,
    RP_METADATA_JWK1
)
from spid_cie_oidc.entity.jwtse import create_jws
from spid_cie_oidc.entity.models import (
    FetchedEntityStatement, 
    TrustChain
)
from spid_cie_oidc.entity.tests.settings import (
    TA_JWK_PRIVATE, 
    TA_SUB,
    ta_conf_data_as_json
)
from spid_cie_oidc.entity.utils import (
    datetime_from_timestamp, 
    exp_from_now,
    iat_now
)

EXP = datetime_from_timestamp(exp_from_now(33))
NOW = datetime_from_timestamp(iat_now())

def create_entity_config():
    JWS_RP = create_jws(RP_CONF_AS_JSON, RP_METADATA_JWK1)
    JWS_TA = create_jws(ta_conf_data_as_json, TA_JWK_PRIVATE)
    return [JWS_RP, JWS_TA]

def create_tc():
    ta_fes = FetchedEntityStatement.objects.create(
        sub=TA_SUB,
        iss=TA_SUB,
        exp=EXP,
        iat=NOW
    )
    return TrustChain.objects.create(
        sub=RP_CONF_AS_JSON["sub"],
        exp=EXP,
        jwks = [],
        metadata=RP_CONF_AS_JSON["metadata"],
        status="valid",
        trust_anchor=ta_fes,
        is_active=True,
    )
class FetchRPTest(TestCase):

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
    
    @override_settings(OIDCFED_IDENTITY_PROVIDERS = {"spid":{"http://127.0.0.1:8000/oidc/op/" :"http://testserver/"}, "cie":{}})
    @override_settings(OIDCFED_TRUST_ANCHOR = [])
    def test_fetch_rp(self):
        self.patcher = patch(
            "spid_cie_oidc.entity.statements.get_entity_configurations", 
            return_value = create_entity_config()
        )
        self.patcher.start()
        self.patcher = patch(
            "spid_cie_oidc.entity.statements.get_http_url", 
            return_value = ['["http://rp-test.it/oidc/rp/"]']
        )
        self.patcher.start()
        self.patcher = patch(
            "spid_cie_oidc.entity.trust_chain_operations.get_or_create_trust_chain", 
            return_value = create_tc()
        )
        self.patcher.start()
        self.exec('fetch_openid_relying_parties', '--from', 'url')
        self.patcher.stop()

