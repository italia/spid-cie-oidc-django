
from django.test import TestCase
from spid_cie_oidc.entity.schemas.resolve_endpoint import ResolveRequest
from .rp_metadata_settings import rp_conf

TA_SUB = "http://testserver.it/"

RESOLVE_REQUEST = {
    "iss": rp_conf["sub"],
    "sub": rp_conf["sub"],
    "anchor" : TA_SUB,
    "format" :"json",
}


class SchemaTest(TestCase):

    def setUp(self) -> None:
        return super().setUp()
    
    def test_resolve_request(self):
        ResolveRequest(**RESOLVE_REQUEST)
