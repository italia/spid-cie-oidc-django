import logging

from django.test import TestCase
from pydantic import ValidationError
from spid_cie_oidc.provider.schemas.op_metadata import OPMetadataCie
from spid_cie_oidc.provider.tests.op_metadata_settings import (
    OP_METADATA_CIE, OP_METADATA_CIE_JWKS_AND_JWKS_URI)

logger = logging.getLogger(__name__)

class OpMetadataTest(TestCase):

    def test_op_metatada_cie(self):
        OPMetadataCie(**OP_METADATA_CIE)

    def test_op_metatada_cie_jwks_and_jwks_uri(self):
        with self.assertRaises(ValidationError):
            OPMetadataCie(**OP_METADATA_CIE_JWKS_AND_JWKS_URI)
