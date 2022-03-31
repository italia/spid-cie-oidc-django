
from unittest.mock import patch

from django.test import TestCase

from spid_cie_oidc.authority.tests.settings import (
    RP_CONF_AS_JSON,
    RP_METADATA_JWK1, 
    rp_conf
)
from spid_cie_oidc.entity.exceptions import InvalidEntityConfiguration
from spid_cie_oidc.entity.jwtse import create_jws
from spid_cie_oidc.entity.tests.settings import (
    TA_JWK_PRIVATE, 
    ta_conf_data,
    ta_conf_data_as_json
)
from spid_cie_oidc.entity.trust_chain import TrustChainBuilder
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


class TrustChainTest(TestCase):

    def setUp(self):
        self.tcb = TrustChainBuilder(
            subject = rp_conf["sub"],
            trust_anchor = ta_conf_data["sub"]
        )

    def test_get_trust_anchor_configuration(self):
        self.patcher = patch(
            "spid_cie_oidc.entity.trust_chain.get_entity_configurations", 
            return_value = create_entity_config()
        )
        self.patcher.start()
        TrustChainBuilder.get_trust_anchor_configuration(self.tcb)
        self.patcher.stop()

    def test_get_subject_configuration_failed(self):
        self.patcher = patch(
            "spid_cie_oidc.entity.trust_chain.get_entity_configurations", 
            return_value = []
        )
        self.patcher.start()
        with self.assertRaises(InvalidEntityConfiguration):
            TrustChainBuilder.get_subject_configuration(self.tcb)
        self.patcher.stop()
