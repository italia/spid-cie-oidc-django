import logging

from django.test import TestCase
from pydantic import ValidationError
from spid_cie_oidc.provider.schemas.jwt import JwtStructure
from spid_cie_oidc.provider.schemas.token_requests import (
    TokenAuthnCodeRequest,
    TokenRefreshRequest,
)

from .token_request_settings import (
    JWT_CLIENT_ASSERTION,
    JWT_CLIENT_ASSERTION_NO_AUD,
    JWT_CLIENT_ASSERTION_NO_CORRECT_AUD,
    JWT_CLIENT_ASSERTION_NO_CORRECT_EXP,
    JWT_CLIENT_ASSERTION_NO_CORRECT_IAT,
    JWT_CLIENT_ASSERTION_NO_CORRECT_ISS,
    JWT_CLIENT_ASSERTION_NO_CORRECT_JTI,
    JWT_CLIENT_ASSERTION_NO_CORRECT_SUB,
    JWT_CLIENT_ASSERTION_NO_EXP,
    JWT_CLIENT_ASSERTION_NO_IAT,
    JWT_CLIENT_ASSERTION_NO_ISS,
    JWT_CLIENT_ASSERTION_NO_JTI,
    JWT_CLIENT_ASSERTION_NO_SUB,
    TOKEN_AUTHN_CODE_REQUEST,
    TOKEN_AUTHN_CODE_REQUEST_NO_CLIENT_ASSERTION,
    TOKEN_AUTHN_CODE_REQUEST_NO_CLIENT_ASSERTION_TYPE,
    TOKEN_AUTHN_CODE_REQUEST_NO_CLIENT_ID,
    TOKEN_AUTHN_CODE_REQUEST_NO_CODE,
    TOKEN_AUTHN_CODE_REQUEST_NO_CODE_VERIFY,
    TOKEN_AUTHN_CODE_REQUEST_NO_CORRECT_CLIENT_ASSERTION,
    TOKEN_AUTHN_CODE_REQUEST_NO_CORRECT_CLIENT_ASSERTION_TYPE,
    TOKEN_AUTHN_CODE_REQUEST_NO_CORRECT_GRANT_TYPE,
    TOKEN_AUTHN_CODE_REQUEST_NO_GRANT_TYPE,
    TOKEN_REFRESH_REQUEST,
    TOKEN_REFRESH_REQUEST_NO_CORRECT_GRANT_TYPE,
    TOKEN_REFRESH_REQUEST_NO_GRANT_TYPE,
)

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
            TokenAuthnCodeRequest(
                **TOKEN_AUTHN_CODE_REQUEST_NO_CORRECT_CLIENT_ASSERTION
            )

    def test_validate_request_no_client_assertion_type(self):
        with self.assertRaises(ValidationError):
            TokenAuthnCodeRequest(**TOKEN_AUTHN_CODE_REQUEST_NO_CLIENT_ASSERTION_TYPE)

    def test_validate_request_no_correct_client_assertion_type(self):
        with self.assertRaises(ValidationError):
            TokenAuthnCodeRequest(
                **TOKEN_AUTHN_CODE_REQUEST_NO_CORRECT_CLIENT_ASSERTION_TYPE
            )

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

    def test_validate_jwt(self):
        JwtStructure(**JWT_CLIENT_ASSERTION)

    def test_validate_jwt_no_iss(self):
        with self.assertRaises(ValidationError):
            JwtStructure(**JWT_CLIENT_ASSERTION_NO_ISS)

    def test_validate_jwt_no_correct_iss(self):
        with self.assertRaises(ValidationError):
            JwtStructure(**JWT_CLIENT_ASSERTION_NO_CORRECT_ISS)

    def test_validate_jwt_no_sub(self):
        with self.assertRaises(ValidationError):
            JwtStructure(**JWT_CLIENT_ASSERTION_NO_SUB)

    def test_validate_jwt_no_correct_sub(self):
        with self.assertRaises(ValidationError):
            JwtStructure(**JWT_CLIENT_ASSERTION_NO_CORRECT_SUB)

    def test_validate_jwt_no_iat(self):
        with self.assertRaises(ValidationError):
            JwtStructure(**JWT_CLIENT_ASSERTION_NO_IAT)

    def test_validate_jwt_no_correct_iat(self):
        with self.assertRaises(ValidationError):
            JwtStructure(**JWT_CLIENT_ASSERTION_NO_CORRECT_IAT)

    def test_validate_jwt_no_exp(self):
        with self.assertRaises(ValidationError):
            JwtStructure(**JWT_CLIENT_ASSERTION_NO_EXP)

    def test_validate_jwt_no_correct_exp(self):
        with self.assertRaises(ValidationError):
            JwtStructure(**JWT_CLIENT_ASSERTION_NO_CORRECT_EXP)

    def test_validate_jwt_no_jti(self):
        with self.assertRaises(ValidationError):
            JwtStructure(**JWT_CLIENT_ASSERTION_NO_JTI)

    def test_validate_jwt_no_correct_jti(self):
        with self.assertRaises(ValidationError):
            JwtStructure(**JWT_CLIENT_ASSERTION_NO_CORRECT_JTI)

    def test_validate_jwt_no_aud(self):
        with self.assertRaises(ValidationError):
            JwtStructure(**JWT_CLIENT_ASSERTION_NO_AUD)

    def test_validate_jwt_no_correct_aud(self):
        with self.assertRaises(ValidationError):
            JwtStructure(**JWT_CLIENT_ASSERTION_NO_CORRECT_AUD)
