from django.test import TestCase
from spid_cie_oidc.authority.tests.settings import (
    RP_METADATA_JWK1,
    RP_METADATA_JWK1_pub
)
from spid_cie_oidc.entity.validators import (
    validate_private_jwks,
    validate_public_jwks
)


class ValidatrTest(TestCase):

    def setUp(self):
        pass

    def test_validate_public_jwks(self):
        with self.assertRaises(Exception):
            validate_public_jwks(RP_METADATA_JWK1)

    def test_validate_private_jwks(self):
        with self.assertRaises(Exception):
            validate_private_jwks(RP_METADATA_JWK1_pub)
