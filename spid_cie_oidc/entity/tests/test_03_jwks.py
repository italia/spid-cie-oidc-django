from django.test import TestCase
from pydantic import ValidationError
from spid_cie_oidc.entity.schemas.jwks import JwksCie, JwksSpid
from spid_cie_oidc.entity.tests.jwks_settings import (
    JWKS,
    JWKS_WITH_N_AND_EC_NO_CORRECT,
    JWKS_WITH_X_AND_RSA_NO_CORRECT,
)


class JwksTest(TestCase):
    def test_jwks_spid(self):
        JwksSpid(**JWKS)

    def test_jwks_cie(self):
        JwksCie(**JWKS)

    def test_jwks_with_n_and_ec_no_correct(self):
        with self.assertRaises(ValidationError):
            JwksSpid(**JWKS_WITH_N_AND_EC_NO_CORRECT)

    def test_jwks_with_e_and_rsa_no_correct(self):
        with self.assertRaises(ValidationError):
            JwksCie(**JWKS_WITH_X_AND_RSA_NO_CORRECT)
