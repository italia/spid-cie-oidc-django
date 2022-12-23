import logging

from django.test import TestCase
from pydantic import ValidationError
from spid_cie_oidc.entity.schemas.op_metadata import OPMetadataCie, OPMetadataSpid
from spid_cie_oidc.entity.tests.op_metadata_settings import (
    OP_METADATA_CIE,
    OP_METADATA_CIE_JWKS_AND_JWKS_URI,
    OP_METADATA_SPID,
    OP_METADATA_SPID_JWKS_AND_JWKS_URI,
    OP_METADATA_SPID_JWKS_EC_NO_CORRECT,
    OP_METADATA_SPID_JWKS_NO_JWKS_URI,
)

logger = logging.getLogger(__name__)


class OpMetadataTest(TestCase):
    def test_op_metatada_cie(self):
        OPMetadataCie(**OP_METADATA_CIE)

    def test_op_metatada_cie_jwks_and_jwks_uri(self):
        self.assertTrue(OPMetadataCie(**OP_METADATA_CIE_JWKS_AND_JWKS_URI))

    def test_op_metatada_spid(self):
        OPMetadataSpid(**OP_METADATA_SPID)

    def test_op_metatada_spid_jwks_and_jwks_uri(self):
        self.assertTrue(OPMetadataSpid(**OP_METADATA_SPID_JWKS_AND_JWKS_URI))

    def test_op_metatada_spid_jwks_no_jwks_uri(self):
        OPMetadataSpid(**OP_METADATA_SPID_JWKS_NO_JWKS_URI)

    def test_op_metatada_spid_jws_ec_no_correct(self):
        with self.assertRaises(ValidationError):
            OPMetadataSpid(**OP_METADATA_SPID_JWKS_EC_NO_CORRECT)
        
