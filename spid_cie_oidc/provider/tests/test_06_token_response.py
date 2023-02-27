import logging

from django.test import TestCase
from pydantic import ValidationError
from spid_cie_oidc.provider.tests.token_response_settings import (
    TOKEN_ERROR_RESPONSE,
    TOKEN_ERROR_RESPONSE_NO_CORRECT_ERROR,
    TOKEN_ERROR_RESPONSE_NO_CORRECT_ERROR_DESCRIPTION,
    TOKEN_ERROR_RESPONSE_NO_ERROR,
    TOKEN_ERROR_RESPONSE_NO_ERROR_DESCRIPTION,
    TOKEN_REFRESH_RESPONSE,
    TOKEN_REFRESH_RESPONSE_NO_CORRECT_REFRESH_TOKEN,
    TOKEN_REFRESH_RESPONSE_NO_REFRESH_TOKEN,
    TOKEN_RESPONSE,
    TOKEN_RESPONSE_NO_ACCESS_TOKEN,
    TOKEN_RESPONSE_NO_CORRECT_ACCESS_TOKEN,
    TOKEN_RESPONSE_NO_CORRECT_TOKEN_TYPE,
    TOKEN_RESPONSE_NO_TOKEN_TYPE,
)
from spid_cie_oidc.provider.schemas.token_response import (
    TokenErrorResponse,
    TokenRefreshResponse,
    TokenResponse,
)

logger = logging.getLogger(__name__)


class TokenResponseTest(TestCase):
    def test_validate_token_response(self):
        TokenResponse(**TOKEN_RESPONSE)

    def test_validate_token_response(self):
        TokenRefreshResponse(**TOKEN_REFRESH_RESPONSE)

    def test_validate_token_response_no_access_token(self):
        with self.assertRaises(ValidationError):
            TokenResponse(**TOKEN_RESPONSE_NO_ACCESS_TOKEN)

    def test_validate_token_response_no_correct_access_token(self):
        with self.assertRaises(ValidationError):
            TokenResponse(**TOKEN_RESPONSE_NO_CORRECT_ACCESS_TOKEN)

    def test_validate_token_response_no_token_type(self):
        with self.assertRaises(ValidationError):
            TokenResponse(**TOKEN_RESPONSE_NO_TOKEN_TYPE)

    def test_validate_token_response_no_correct_token_type(self):
        with self.assertRaises(ValidationError):
            TokenResponse(**TOKEN_RESPONSE_NO_CORRECT_TOKEN_TYPE)

    def test_validate_token_refresh_response_no_refresh_token(self):
        with self.assertRaises(ValidationError):
            TokenRefreshResponse(**TOKEN_REFRESH_RESPONSE_NO_REFRESH_TOKEN)

    def test_validate_token_refresh_response_no_correct_refresh_token(self):
        with self.assertRaises(ValidationError):
            TokenRefreshResponse(**TOKEN_REFRESH_RESPONSE_NO_CORRECT_REFRESH_TOKEN)

    def test_validate_token_error_response(self):
        TokenErrorResponse(**TOKEN_ERROR_RESPONSE)

    def test_validate_token_error_no_error(self):
        with self.assertRaises(ValidationError):
            TokenErrorResponse(**TOKEN_ERROR_RESPONSE_NO_ERROR)

    def test_validate_token_error_no_correct_error(self):
        with self.assertRaises(ValidationError):
            TokenErrorResponse(**TOKEN_ERROR_RESPONSE_NO_CORRECT_ERROR)

    def test_validate_token_error_no_error_description(self):
        with self.assertRaises(ValidationError):
            TokenErrorResponse(**TOKEN_ERROR_RESPONSE_NO_ERROR_DESCRIPTION)

    def test_validate_token_error_no_correct_error_description(self):
        with self.assertRaises(ValidationError):
            TokenErrorResponse(**TOKEN_ERROR_RESPONSE_NO_CORRECT_ERROR_DESCRIPTION)
