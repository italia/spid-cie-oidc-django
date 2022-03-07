from django.test import TestCase
from pydantic import ValidationError
from spid_cie_oidc.onboarding.tests.introspection_response_settings import (
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
    INTROSPECTION_RESPONSE_NO_CORRECT_AUD,
    INTROSPECTION_RESPONSE_NO_CORRECT_CLIENT_ID,
    INTROSPECTION_RESPONSE_NO_CORRECT_EXP,
    INTROSPECTION_RESPONSE_NO_CORRECT_ISS,
    INTROSPECTION_RESPONSE_NO_CORRECT_SCOPE,
    INTROSPECTION_RESPONSE_NO_CORRECT_SUB,
)
from spid_cie_oidc.onboarding.schemas.introspection_response import (
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

    def test_validate_introspection_response_no_correct_scope(self):
        with self.assertRaises(ValidationError):
            IntrospectionResponse(**INTROSPECTION_RESPONSE_NO_CORRECT_SCOPE)

    def test_validate_introspection_response_no_correct_exp(self):
        with self.assertRaises(ValidationError):
            IntrospectionResponse(**INTROSPECTION_RESPONSE_NO_CORRECT_EXP)

    def test_validate_introspection_response_no_correct_sub(self):
        with self.assertRaises(ValidationError):
            IntrospectionResponse(**INTROSPECTION_RESPONSE_NO_CORRECT_SUB)

    def test_validate_introspection_response_no_correct_client_id(self):
        with self.assertRaises(ValidationError):
            IntrospectionResponse(**INTROSPECTION_RESPONSE_NO_CORRECT_CLIENT_ID)

    def test_validate_introspection_response_no_correct_iss(self):
        with self.assertRaises(ValidationError):
            IntrospectionResponse(**INTROSPECTION_RESPONSE_NO_CORRECT_ISS)

    def test_validate_introspection_response_no_correct_aud(self):
        with self.assertRaises(ValidationError):
            IntrospectionResponse(**INTROSPECTION_RESPONSE_NO_CORRECT_AUD)

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
