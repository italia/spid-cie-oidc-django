
from copy import deepcopy
from unittest.mock import patch

from django.test import TestCase
from spid_cie_oidc.authority.tests.settings import (
    RP_CONF_AS_JSON,
     RP_METADATA_JWK1
)
from spid_cie_oidc.authority.utils import random_token
from spid_cie_oidc.authority.validators import validate_entity_configuration
from spid_cie_oidc.entity.exceptions import MissingAuthorityHintsClaim, NotDescendant
from spid_cie_oidc.entity.jwtse import create_jws
from spid_cie_oidc.entity.models import FederationEntityConfiguration
from spid_cie_oidc.entity.tests.settings import ta_conf_data

JWS = create_jws(RP_CONF_AS_JSON, RP_METADATA_JWK1)
RP_CONF_AS_JSON_NO_HINTS = deepcopy(RP_CONF_AS_JSON)
RP_CONF_AS_JSON_NO_HINTS.pop("authority_hints")
JWS_NO_HINTS = create_jws(RP_CONF_AS_JSON_NO_HINTS, RP_METADATA_JWK1)
RP_CONF_AS_JSON_WRONG_HINTS = deepcopy(RP_CONF_AS_JSON)
RP_CONF_AS_JSON_WRONG_HINTS["authority_hints"] = ["http://wrong.url.it"]
JWS_WRONG_HINTS = create_jws(RP_CONF_AS_JSON_WRONG_HINTS, RP_METADATA_JWK1)

class ValidatorTest(TestCase):

    def setUp(self):
        self.ta_conf = FederationEntityConfiguration.objects.create(**ta_conf_data)

    @patch("spid_cie_oidc.authority.validators.get_entity_configurations", return_value = [JWS])
    def test_validator(self, mocked):
        validate_entity_configuration(["url_entity"])

    @patch("spid_cie_oidc.authority.validators.get_entity_configurations", return_value = [JWS_NO_HINTS])
    def test_validator_no_hints(self, mocked):
        with self.assertRaises(MissingAuthorityHintsClaim):
            validate_entity_configuration(["url_entity"])

    @patch("spid_cie_oidc.authority.validators.get_entity_configurations", return_value = [JWS_WRONG_HINTS])
    def test_validator_no_descendant(self, mocked):
        with self.assertRaises(NotDescendant):
            validate_entity_configuration(["url_entity"])


class UtilityTests(TestCase):

    def test_random_token(self):
        self.assertTrue(random_token())