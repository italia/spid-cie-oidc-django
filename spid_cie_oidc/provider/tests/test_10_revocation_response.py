from django.test import TestCase
from pydantic import ValidationError
from spid_cie_oidc.provider.tests.revocation_response_settings import (
    REVOCATION_RESPONSE_CIE,
    REVOCATION_RESPONSE_CIE_NO_CORRECT_ERROR,
    REVOCATION_RESPONSE_CIE_NO_CORRECT_ERROR_DESCRIPTION,
    REVOCATION_RESPONSE_CIE_NO_ERROR,
    REVOCATION_RESPONSE_CIE_NO_ERROR_DESCRIPTION,
)
from spid_cie_oidc.provider.schemas.revocation_response import (
    RevocationErrorResponse,
)


class RevocationResponseTest(TestCase):
    def test_validate_revocation_response(self):
        RevocationErrorResponse(**REVOCATION_RESPONSE_CIE)

    def test_validate_revocation_response_no_error(self):
        with self.assertRaises(ValidationError):
            RevocationErrorResponse(**REVOCATION_RESPONSE_CIE_NO_ERROR)

    def test_validate_revocation_response_no_correct_error(self):
        with self.assertRaises(ValidationError):
            RevocationErrorResponse(**REVOCATION_RESPONSE_CIE_NO_CORRECT_ERROR)

    def test_validate_revocation_response_no_error_description(self):
        with self.assertRaises(ValidationError):
            RevocationErrorResponse(**REVOCATION_RESPONSE_CIE_NO_ERROR_DESCRIPTION)

    def test_validate_revocation_response_no_correct_error_description(self):
        with self.assertRaises(ValidationError):
            RevocationErrorResponse(
                **REVOCATION_RESPONSE_CIE_NO_CORRECT_ERROR_DESCRIPTION
            )
