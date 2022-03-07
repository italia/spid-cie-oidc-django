from django.test import TestCase
from pydantic import ValidationError
from spid_cie_oidc.entity.schemas.rp_metadata import RPMetadataCie, RPMetadataSpid
from spid_cie_oidc.entity.tests.rp_metadata_settings import (
    RP_METADATA_CIE,
    RP_METADATA_SPID,
    RP_METADATA_SPID_JWKS_AND_JWKS_URI,
    RP_METADATA_SPID_NO_REDIRECT_URIS,
)


class RPMetadataTest(TestCase):
    def test_rp_metadataCie(self):
        RPMetadataCie(**RP_METADATA_CIE)

    def test_rp_metadataSpid(self):
        RPMetadataSpid(**RP_METADATA_SPID)

    def test_rp_metadataSpid_no_redirect_uris(self):
        with self.assertRaises(ValidationError):
            RPMetadataSpid(**RP_METADATA_SPID_NO_REDIRECT_URIS)

    def test_rp_metadataSpid_no_jwks_and_jkws_uri(self):
        with self.assertRaises(ValidationError):
            RPMetadataSpid(**RP_METADATA_SPID_JWKS_AND_JWKS_URI)
