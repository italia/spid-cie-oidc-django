import logging

from django.test import TestCase
from pydantic import ValidationError
from spid_cie_oidc.provider.schemas.authn_response import (
    AuthenticationErrorResponse,
    AuthenticationErrorResponseCie,
    AuthenticationResponse,
    AuthenticationResponseCie,
)

from .authn_responses_settings import (
    AUTHN_ERROR_RESPONSE_CIE,
    AUTHN_ERROR_RESPONSE_CIE_NO_CORRECT_ISS,
    AUTHN_ERROR_RESPONSE_CIE_NO_ISS,
    AUTHN_ERROR_RESPONSE_SPID,
    AUTHN_ERROR_RESPONSE_SPID_NO_CODE,
    AUTHN_ERROR_RESPONSE_SPID_NO_CORRECT_STATE,
    AUTHN_ERROR_RESPONSE_SPID_NO_STATE,
    AUTHN_RESPONSE_CIE,
    AUTHN_RESPONSE_CIE_NO_CORRECT_ISS,
    AUTHN_RESPONSE_CIE_NO_ISS,
    AUTHN_RESPONSE_SPID,
    AUTHN_RESPONSE_SPID_NO_CODE,
    AUTHN_RESPONSE_SPID_NO_CORRECT_STATE,
    AUTHN_RESPONSE_SPID_NO_STATE,
)

logger = logging.getLogger(__name__)


class AuthResponseTest(TestCase):
    def test_validate_response_spid(self):
        AuthenticationResponse(**AUTHN_RESPONSE_SPID)

    def test_validate_response_spid_no_code(self):
        with self.assertRaises(ValidationError):
            AuthenticationResponse(**AUTHN_RESPONSE_SPID_NO_CODE)

    def test_validate_response_spid_no_state(self):
        with self.assertRaises(ValidationError):
            AuthenticationResponse(**AUTHN_RESPONSE_SPID_NO_STATE)

    def test_validate_response_spid_no_correct_state(self):
        with self.assertRaises(ValidationError):
            AuthenticationResponse(**AUTHN_RESPONSE_SPID_NO_CORRECT_STATE)

    def test_validate_response_cie(self):
        AuthenticationResponseCie(**AUTHN_RESPONSE_CIE)

    def test_validate_response_cie_no_iss(self):
        with self.assertRaises(ValidationError):
            AuthenticationResponseCie(**AUTHN_RESPONSE_CIE_NO_ISS)

    def test_validate_response_cie_no_correct_iss(self):
        with self.assertRaises(ValidationError):
            AuthenticationResponseCie(**AUTHN_RESPONSE_CIE_NO_CORRECT_ISS)

    def test_validate_error_response_spid(self):
        AuthenticationErrorResponse(**AUTHN_ERROR_RESPONSE_SPID)

    def test_validate_error_response_spid_no_code(self):
        with self.assertRaises(ValidationError):
            AuthenticationErrorResponse(**AUTHN_ERROR_RESPONSE_SPID_NO_CODE)

    def test_validate_error_response_spid_no_state(self):
        with self.assertRaises(ValidationError):
            AuthenticationErrorResponse(**AUTHN_ERROR_RESPONSE_SPID_NO_STATE)

    def test_validate_error_response_spid_no_correct_state(self):
        with self.assertRaises(ValidationError):
            AuthenticationErrorResponse(**AUTHN_ERROR_RESPONSE_SPID_NO_CORRECT_STATE)

    def test_validate_error_response_cie(self):
        AuthenticationErrorResponseCie(**AUTHN_ERROR_RESPONSE_CIE)

    def test_validate_error_response_spid_no_iss(self):
        with self.assertRaises(ValidationError):
            AuthenticationErrorResponseCie(**AUTHN_ERROR_RESPONSE_CIE_NO_ISS)

    def test_validate_error_response_spid_no_correct_iss(self):
        with self.assertRaises(ValidationError):
            AuthenticationErrorResponseCie(**AUTHN_ERROR_RESPONSE_CIE_NO_CORRECT_ISS)
