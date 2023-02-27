
from django.test import TestCase
from spid_cie_oidc.authority.schemas.advanced_entity_list_endpoint import AdvancedEntityListRequest
from spid_cie_oidc.authority.schemas.fetch_endpoint_request import FetchRequest
from spid_cie_oidc.authority.schemas.list_endpoint import ListRequest
from spid_cie_oidc.authority.schemas.trust_mark_status_endpoint import TrustMarkRequest
from spid_cie_oidc.authority.tests.settings import (
    FETCH_REQUEST,
    LIST_REQUEST,
    TRUST_MARK_REQUEST,
    ADVANCED_LIST_REQUEST,
    TRUST_MARK_REQUEST_NO_SUB_ID,
    TRUST_MARK_REQUEST_NO_TRUST_MARK,
    TRUST_MARK_REQUEST_TRUST_MARK_NO_ID_NO_TRUST_MARK,
    TRUST_MARK_REQUEST_TRUST_MARK_NO_SUB,
    TRUST_MARK_REQUEST_TRUST_MARK_NO_SUB_NO_TRUST_MARK,
)

class SchemaTest(TestCase):

    def setUp(self) -> None:
        return super().setUp()
    
    def test_fetch_request(self):
        FetchRequest(**FETCH_REQUEST)

    def test_list_request(self):
        ListRequest(**LIST_REQUEST)

    def test_trust_mark_request(self):
        TrustMarkRequest(**TRUST_MARK_REQUEST)

    def test_trust_mark_request_no_sub_id(self):
        TrustMarkRequest(**TRUST_MARK_REQUEST_NO_SUB_ID)

    def test_trust_mark_request_no_rust_mark(self):
        TrustMarkRequest(**TRUST_MARK_REQUEST_NO_TRUST_MARK)

    def test_trust_mark_request_no_sub(self):
        TrustMarkRequest(**TRUST_MARK_REQUEST_TRUST_MARK_NO_SUB)

    def test_trust_mark_request_no_id_no_tust_mark(self):
        with self.assertRaises(ValueError):
            TrustMarkRequest(**TRUST_MARK_REQUEST_TRUST_MARK_NO_ID_NO_TRUST_MARK)
        
    def test_trust_mark_request_no_sub_no_tust_mark(self):
        with self.assertRaises(ValueError):
            TrustMarkRequest(**TRUST_MARK_REQUEST_TRUST_MARK_NO_SUB_NO_TRUST_MARK)

    def test_advanced_list_request(self):
        AdvancedEntityListRequest(**ADVANCED_LIST_REQUEST)
