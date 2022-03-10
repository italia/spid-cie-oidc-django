
from unittest.mock import patch

from django.test import TestCase, override_settings
from spid_cie_oidc.authority.tests.settings import (
    RP_CONF_AS_JSON,
     RP_METADATA_JWK1
)
from spid_cie_oidc.authority.validators import validate_entity_configuration
from spid_cie_oidc.entity.jwtse import create_jws

JWS = create_jws(RP_CONF_AS_JSON, RP_METADATA_JWK1)

class ValidatorTest(TestCase):

    def setUp(self):
        pass

    @patch("spid_cie_oidc.authority.validators.get_entity_configurations", return_value = [JWS])
    @patch("spid_cie_oidc.authority.validators.OIDCFED_TRUST_ANCHORS", ["http://testserver/"])
    def test_validator(self, mocked):
        validate_entity_configuration(["url_entity"])

    