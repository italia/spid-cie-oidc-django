from django.test import TestCase
from pydantic import ValidationError
from spid_cie_oidc.provider.tests.introspection_request_settings import (
    INTROSPECTION_REQUEST,
    INTROSPECTION_REQUEST_NO_CLIENT_ASSERTION,
    INTROSPECTION_REQUEST_NO_CLIENT_ASSERTION_TYPE,
    INTROSPECTION_REQUEST_NO_CLIENT_ID,
    INTROSPECTION_REQUEST_NO_CORRECT_CLIENT_ASSERTION,
    INTROSPECTION_REQUEST_NO_CORRECT_CLIENT_ASSERTION_TYPE,
    INTROSPECTION_REQUEST_NO_CORRECT_CLIENT_ID,
    INTROSPECTION_REQUEST_NO_CORRECT_TOKEN,
    INTROSPECTION_REQUEST_NO_TOKEN,
)
from spid_cie_oidc.provider.schemas.introspection_request import IntrospectionRequest


class IntrospectionRequestTest(TestCase):
    def test_validate_introspection_request(self):
        IntrospectionRequest(**INTROSPECTION_REQUEST)

    def test_validate_introspection_request_no_client_assertion(self):
        with self.assertRaises(ValidationError):
            IntrospectionRequest(**INTROSPECTION_REQUEST_NO_CLIENT_ASSERTION)

    def test_validate_introspection_request_no_correct_client_assertion(self):
        with self.assertRaises(ValidationError):
            IntrospectionRequest(**INTROSPECTION_REQUEST_NO_CORRECT_CLIENT_ASSERTION)

    def test_validate_introspection_request_no_client_assertion_type(self):
        with self.assertRaises(ValidationError):
            IntrospectionRequest(**INTROSPECTION_REQUEST_NO_CLIENT_ASSERTION_TYPE)

    def test_validate_introspection_request_no_correct_client_assertion_type(self):
        with self.assertRaises(ValidationError):
            IntrospectionRequest(
                **INTROSPECTION_REQUEST_NO_CORRECT_CLIENT_ASSERTION_TYPE
            )

    def test_validate_introspection_request_no_client_id(self):
        with self.assertRaises(ValidationError):
            IntrospectionRequest(**INTROSPECTION_REQUEST_NO_CLIENT_ID)

    def test_validate_introspection_request_no_correct_client_id(self):
        with self.assertRaises(ValidationError):
            IntrospectionRequest(**INTROSPECTION_REQUEST_NO_CORRECT_CLIENT_ID)

    def test_validate_introspection_request_no_token(self):
        with self.assertRaises(ValidationError):
            IntrospectionRequest(**INTROSPECTION_REQUEST_NO_TOKEN)

    def test_validate_introspection_request_no_correct_token(self):
        with self.assertRaises(ValidationError):
            IntrospectionRequest(**INTROSPECTION_REQUEST_NO_CORRECT_TOKEN)
