from django.test import TestCase
from pydantic import ValidationError
from spid_cie_oidc.onboarding.tests.revocation_request_settings import (
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
from spid_cie_oidc.onboarding.schemas.revocation_request import RevocationRequest


class RevocationRequestTest(TestCase):
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
