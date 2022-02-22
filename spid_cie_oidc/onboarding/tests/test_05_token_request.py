import logging

from django.test import TestCase
from pydantic import ValidationError
from spid_cie_oidc.onboarding.validators.token_requests import (
    TokenAuthnCodeRequest, TokenRefreshRequest)

from .token_request_settings import (
    TOKEN_AUTHN_CODE_REQUEST, TOKEN_AUTHN_CODE_REQUEST_NO_CLIENT_ASSERTION,
    TOKEN_AUTHN_CODE_REQUEST_NO_CLIENT_ASSERTION_TYPE,
    TOKEN_AUTHN_CODE_REQUEST_NO_CLIENT_ID, TOKEN_AUTHN_CODE_REQUEST_NO_CODE,
    TOKEN_AUTHN_CODE_REQUEST_NO_CODE_VERIFY,
    TOKEN_AUTHN_CODE_REQUEST_NO_CORRECT_CLIENT_ASSERTION,
    TOKEN_AUTHN_CODE_REQUEST_NO_CORRECT_CLIENT_ASSERTION_TYPE,
    TOKEN_AUTHN_CODE_REQUEST_NO_CORRECT_GRANT_TYPE,
    TOKEN_AUTHN_CODE_REQUEST_NO_GRANT_TYPE, TOKEN_REFRESH_REQUEST,
    TOKEN_REFRESH_REQUEST_NO_CORRECT_GRANT_TYPE,
    TOKEN_REFRESH_REQUEST_NO_GRANT_TYPE)

logger = logging.getLogger(__name__)


class TokenRequestTest(TestCase):

    def test_validate_request(self):
        TokenAuthnCodeRequest(**TOKEN_AUTHN_CODE_REQUEST)
    
    def test_validate_request_no_client(self):
        with self.assertRaises(ValidationError):
            TokenAuthnCodeRequest(**TOKEN_AUTHN_CODE_REQUEST_NO_CLIENT_ID)

    def test_validate_request_no_client_assertion(self):
        with self.assertRaises(ValidationError):
            TokenAuthnCodeRequest(**TOKEN_AUTHN_CODE_REQUEST_NO_CLIENT_ASSERTION)

    def test_validate_request_no_correct_client_assertion(self):
        with self.assertRaises(ValidationError):
            TokenAuthnCodeRequest(**TOKEN_AUTHN_CODE_REQUEST_NO_CORRECT_CLIENT_ASSERTION)

    def test_validate_request_no_client_assertion_type(self):
        with self.assertRaises(ValidationError):
            TokenAuthnCodeRequest(**TOKEN_AUTHN_CODE_REQUEST_NO_CLIENT_ASSERTION_TYPE)

    def test_validate_request_no_correct_client_assertion_type(self):
        with self.assertRaises(ValidationError):
            TokenAuthnCodeRequest(**TOKEN_AUTHN_CODE_REQUEST_NO_CORRECT_CLIENT_ASSERTION_TYPE)

    def test_validate_request_no_code(self):
        with self.assertRaises(ValidationError):
            TokenAuthnCodeRequest(**TOKEN_AUTHN_CODE_REQUEST_NO_CODE)

    def test_validate_request_no_code_verify(self):
        with self.assertRaises(ValidationError):
            TokenAuthnCodeRequest(**TOKEN_AUTHN_CODE_REQUEST_NO_CODE_VERIFY)

    def test_validate_request_no_grant_type(self):
        with self.assertRaises(ValidationError):
            TokenAuthnCodeRequest(**TOKEN_AUTHN_CODE_REQUEST_NO_GRANT_TYPE)

    def test_validate_request_no_correct_grant_type(self):
        with self.assertRaises(ValidationError):
            TokenAuthnCodeRequest(**TOKEN_AUTHN_CODE_REQUEST_NO_CORRECT_GRANT_TYPE)

    def test_validate_refresh_request(self):
        TokenRefreshRequest(**TOKEN_REFRESH_REQUEST)

    def test_validate_refresh_request_no_grant_type(self):
        with self.assertRaises(ValidationError):
            TokenRefreshRequest(**TOKEN_REFRESH_REQUEST_NO_GRANT_TYPE)

    def test_validate_refresh_request_no_correct_grant_type(self):
        with self.assertRaises(ValidationError):
            TokenRefreshRequest(**TOKEN_REFRESH_REQUEST_NO_CORRECT_GRANT_TYPE)

