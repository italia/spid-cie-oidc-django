from django.test import TestCase
from spid_cie_oidc.entity.schemas.fa_metadata import FAMetadata
from spid_cie_oidc.entity.tests.fa_metadata_settings import FA_METADATA


class FAMetadatTest(TestCase):
    def test_fa_metadata(self):
        FAMetadata(**FA_METADATA)
