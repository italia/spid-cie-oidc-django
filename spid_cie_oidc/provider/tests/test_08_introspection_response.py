from django.test import TestCase
from pydantic import ValidationError
from spid_cie_oidc.provider.tests.introspection_response_settings import (
    INTROSPECTION_ERROR_RESPONSE,
    INTROSPECTION_ERROR_RESPONSE_CIE_NO_CORRECT_ERROR,
    INTROSPECTION_ERROR_RESPONSE_CIE_NO_ERROR,
    INTROSPECTION_ERROR_RESPONSE_NO_CORRECT_ERROR_DESCRIPTION,
    INTROSPECTION_ERROR_RESPONSE_NO_ERROR_DESCRIPTION,
    INTROSPECTION_ERROR_RESPONSE_SPID_NO_CORRECT_ERROR,
    INTROSPECTION_ERROR_RESPONSE_SPID_NO_ERROR,
    INTROSPECTION_RESPONSE,
    INTROSPECTION_RESPONSE_NO_ACTIVE,
    INTROSPECTION_RESPONSE_NO_CORRECT_ACTIVE,
)
from spid_cie_oidc.provider.schemas.introspection_response import (
    IntrospectionErrorResponse,
    IntrospectionErrorResponseCie,
    IntrospectionErrorResponseSpid,
    IntrospectionResponse,
)


class IntrospectionResponseTest(TestCase):
    def test_validate_introspection_response(self):
        IntrospectionResponse(**INTROSPECTION_RESPONSE)

    def test_validate_introspection_response_no_active(self):
        with self.assertRaises(ValidationError):
            IntrospectionResponse(**INTROSPECTION_RESPONSE_NO_ACTIVE)

    def test_validate_introspection_response_no_correct_active(self):
        with self.assertRaises(ValidationError):
            IntrospectionResponse(**INTROSPECTION_RESPONSE_NO_CORRECT_ACTIVE)

    def test_validate_introspection_error_response(self):
        IntrospectionErrorResponse(**INTROSPECTION_ERROR_RESPONSE)

    def test_validate_introspection_response_spid_no_error(self):
        with self.assertRaises(ValidationError):
            IntrospectionErrorResponseSpid(**INTROSPECTION_ERROR_RESPONSE_SPID_NO_ERROR)

    def test_validate_introspection_response_spid_no_correct_error(self):
        with self.assertRaises(ValidationError):
            IntrospectionErrorResponseSpid(
                **INTROSPECTION_ERROR_RESPONSE_SPID_NO_CORRECT_ERROR
            )

    def test_validate_introspection_response_cie_no_error(self):
        with self.assertRaises(ValidationError):
            IntrospectionErrorResponseCie(**INTROSPECTION_ERROR_RESPONSE_CIE_NO_ERROR)

    def test_validate_introspection_response_cie_no_correct_error(self):
        with self.assertRaises(ValidationError):
            IntrospectionErrorResponseCie(
                **INTROSPECTION_ERROR_RESPONSE_CIE_NO_CORRECT_ERROR
            )

    def test_validate_introspection_response_no_error_description(self):
        with self.assertRaises(ValidationError):
            IntrospectionErrorResponse(
                **INTROSPECTION_ERROR_RESPONSE_NO_ERROR_DESCRIPTION
            )

    def test_validate_introspection_response_no_correct_error_description(self):
        with self.assertRaises(ValidationError):
            IntrospectionErrorResponse(
                **INTROSPECTION_ERROR_RESPONSE_NO_CORRECT_ERROR_DESCRIPTION
            )
