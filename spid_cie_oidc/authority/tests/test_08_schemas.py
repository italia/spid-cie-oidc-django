
from django.test import TestCase
from spid_cie_oidc.authority.schemas.advanced_entity_list_endpoint import AdvancedEntityListRequest
from spid_cie_oidc.authority.schemas.fetch_endpoint_request import FetchRequest
from spid_cie_oidc.authority.schemas.list_endpoint import ListRequest
from spid_cie_oidc.authority.schemas.resolve_endpoint import ResolveRequest
from spid_cie_oidc.authority.schemas.trust_mark_status_endpoint import TrustMarkRequest
from spid_cie_oidc.authority.tests.settings import (
    RESOLVE_REQUEST,
    FETCH_REQUEST,
    LIST_REQUEST,
    TRUST_MARK_REQUEST,
    ADVANCED_LIST_REQUEST,
)

class SchemaTest(TestCase):

    def setUp(self) -> None:
        return super().setUp()
    
    def test_resolve_request(self):
        ResolveRequest(**RESOLVE_REQUEST)
    
    def test_fetch_request(self):
        FetchRequest(**FETCH_REQUEST)

    def test_list_request(self):
        ListRequest(**LIST_REQUEST)

    def test_trust_mark_request(self):
        TrustMarkRequest(**TRUST_MARK_REQUEST)

    def test_advanced_list_request(self):
        AdvancedEntityListRequest(**ADVANCED_LIST_REQUEST)
