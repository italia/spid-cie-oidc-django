from copy import deepcopy
from django.test import TestCase
from pydantic import ValidationError
from spid_cie_oidc.provider.tests.revocation_request_settings import (
    REVOCATION_REQUEST,
    REVOCATION_REQUEST_NO_CLIENT_ASSERTION,
    REVOCATION_REQUEST_NO_CLIENT_ASSERTION_TYPE,
    REVOCATION_REQUEST_NO_CLIENT_ID,
    REVOCATION_REQUEST_NO_CORRECT_CLIENT_ASSERTION,
    REVOCATION_REQUEST_NO_CORRECT_CLIENT_ASSERTION_TYPE,
    REVOCATION_REQUEST_NO_CORRECT_CLIENT_ID,
    REVOCATION_REQUEST_NO_CORRECT_TOKEN,
    REVOCATION_REQUEST_NO_TOKEN,
)
from spid_cie_oidc.entity.models import (
    FederationEntityConfiguration
)
from spid_cie_oidc.provider.schemas.revocation_request import RevocationRequest
from spid_cie_oidc.provider.tests.settings import (
    op_conf
)

class RevocationRequestTest(TestCase):
    
    def setUp(self):
        self.op_local_conf = deepcopy(op_conf)
        FederationEntityConfiguration.objects.create(**self.op_local_conf)
    
    def test_validate_revocation_request(self):
        RevocationRequest(**REVOCATION_REQUEST)

    def test_validate_revocation_request_no_client_assertion(self):
        with self.assertRaises(ValidationError):
            RevocationRequest(**REVOCATION_REQUEST_NO_CLIENT_ASSERTION)

    def test_validate_revocation_request_no_correct_client_assertion(self):
        with self.assertRaises(ValidationError):
            RevocationRequest(**REVOCATION_REQUEST_NO_CORRECT_CLIENT_ASSERTION)

    def test_validate_revocation_request_no_client_assertion_type(self):
        with self.assertRaises(ValidationError):
            RevocationRequest(**REVOCATION_REQUEST_NO_CLIENT_ASSERTION_TYPE)

    def test_validate_revocation_request_no_correct_client_assertion_type(self):
        with self.assertRaises(ValidationError):
            RevocationRequest(**REVOCATION_REQUEST_NO_CORRECT_CLIENT_ASSERTION_TYPE)

    def test_validate_revocation_request_no_client_id(self):
        with self.assertRaises(ValidationError):
            RevocationRequest(**REVOCATION_REQUEST_NO_CLIENT_ID)

    def test_validate_revocation_request_no_correct_client_id(self):
        with self.assertRaises(ValidationError):
            RevocationRequest(**REVOCATION_REQUEST_NO_CORRECT_CLIENT_ID)

    def test_validate_revocation_request_no_token(self):
        with self.assertRaises(ValidationError):
            RevocationRequest(**REVOCATION_REQUEST_NO_TOKEN)

    def test_validate_revocation_request_no_correct_token(self):
        with self.assertRaises(ValidationError):
            RevocationRequest(**REVOCATION_REQUEST_NO_CORRECT_TOKEN)
