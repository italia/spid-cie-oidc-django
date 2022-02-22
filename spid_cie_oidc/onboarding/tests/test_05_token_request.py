import logging

from django.test import TestCase
from pydantic import ValidationError
from spid_cie_oidc.onboarding.validators.token_requests import (
    JwtClientAssertionStructureCie, JwtClientAssertionStructureSpid,
    TokenAuthnCodeRequest, TokenRefreshRequest)

from .token_request_settings import (
    JWT_CLIENT_ASSERTION_CIE, JWT_CLIENT_ASSERTION_CIE_NO_AUD,
    JWT_CLIENT_ASSERTION_CIE_NO_CORRECT_AUD, JWT_CLIENT_ASSERTION_SPID,
    JWT_CLIENT_ASSERTION_SPID_NO_AUD, JWT_CLIENT_ASSERTION_SPID_NO_CORRECT_AUD,
    JWT_CLIENT_ASSERTION_SPID_NO_CORRECT_EXP,
    JWT_CLIENT_ASSERTION_SPID_NO_CORRECT_IAT,
    JWT_CLIENT_ASSERTION_SPID_NO_CORRECT_ISS,
    JWT_CLIENT_ASSERTION_SPID_NO_CORRECT_JTI,
    JWT_CLIENT_ASSERTION_SPID_NO_CORRECT_SUB, JWT_CLIENT_ASSERTION_SPID_NO_EXP,
    JWT_CLIENT_ASSERTION_SPID_NO_IAT, JWT_CLIENT_ASSERTION_SPID_NO_ISS,
    JWT_CLIENT_ASSERTION_SPID_NO_JTI, JWT_CLIENT_ASSERTION_SPID_NO_SUB,
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

    def test_validate_jwt_spid(self):
        JwtClientAssertionStructureSpid(**JWT_CLIENT_ASSERTION_SPID)

    def test_validate_jwt_cie(self):
        JwtClientAssertionStructureCie(**JWT_CLIENT_ASSERTION_CIE)

    def test_validate_jwt_spid_no_iss(self):
        with self.assertRaises(ValidationError):
            JwtClientAssertionStructureSpid(**JWT_CLIENT_ASSERTION_SPID_NO_ISS)

    def test_validate_jwt_spid_no_correct_iss(self):
        with self.assertRaises(ValidationError):
            JwtClientAssertionStructureSpid(**JWT_CLIENT_ASSERTION_SPID_NO_CORRECT_ISS)

    def test_validate_jwt_spid_no_sub(self):
        with self.assertRaises(ValidationError):
            JwtClientAssertionStructureSpid(**JWT_CLIENT_ASSERTION_SPID_NO_SUB)

    def test_validate_jwt_spid_no_correct_sub(self):
        with self.assertRaises(ValidationError):
            JwtClientAssertionStructureSpid(**JWT_CLIENT_ASSERTION_SPID_NO_CORRECT_SUB)

    def test_validate_jwt_spid_no_iat(self):
        with self.assertRaises(ValidationError):
            JwtClientAssertionStructureSpid(**JWT_CLIENT_ASSERTION_SPID_NO_IAT)

    def test_validate_jwt_spid_no_correct_iat(self):
        with self.assertRaises(ValidationError):
            JwtClientAssertionStructureSpid(**JWT_CLIENT_ASSERTION_SPID_NO_CORRECT_IAT)

    def test_validate_jwt_spid_no_exp(self):
        with self.assertRaises(ValidationError):
            JwtClientAssertionStructureSpid(**JWT_CLIENT_ASSERTION_SPID_NO_EXP)

    def test_validate_jwt_spid_no_correct_exp(self):
        with self.assertRaises(ValidationError):
            JwtClientAssertionStructureSpid(**JWT_CLIENT_ASSERTION_SPID_NO_CORRECT_EXP)

    def test_validate_jwt_spid_no_jti(self):
        with self.assertRaises(ValidationError):
            JwtClientAssertionStructureSpid(**JWT_CLIENT_ASSERTION_SPID_NO_JTI)

    def test_validate_jwt_spid_no_correct_jti(self):
        with self.assertRaises(ValidationError):
            JwtClientAssertionStructureSpid(**JWT_CLIENT_ASSERTION_SPID_NO_CORRECT_JTI)

    def test_validate_jwt_spid_no_aud(self):
        with self.assertRaises(ValidationError):
            JwtClientAssertionStructureSpid(**JWT_CLIENT_ASSERTION_SPID_NO_AUD)

    def test_validate_jwt_spid_no_correct_aud(self):
        with self.assertRaises(ValidationError):
            JwtClientAssertionStructureSpid(**JWT_CLIENT_ASSERTION_SPID_NO_CORRECT_AUD)

    def test_validate_jwt_cie_no_aud(self):
        with self.assertRaises(ValidationError):
            JwtClientAssertionStructureCie(**JWT_CLIENT_ASSERTION_CIE_NO_AUD)

    def test_validate_jwt_cie_no_correct_aud(self):
        with self.assertRaises(ValidationError):
            JwtClientAssertionStructureCie(**JWT_CLIENT_ASSERTION_CIE_NO_CORRECT_AUD)

