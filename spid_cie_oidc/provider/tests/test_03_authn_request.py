import logging

from django.test import TestCase
from pydantic import ValidationError
from spid_cie_oidc.provider.schemas.authn_requests import (
    AuthenticationRequestCie,
    AuthenticationRequestSpid,
)

from .authn_request_settings import (
    AUTHN_REQUEST_CIE,
    AUTHN_REQUEST_CIE_NO_ACR_VALUES,
    AUTHN_REQUEST_CIE_NO_CORRECT_ACR_VALUES,
    AUTHN_REQUEST_CIE_NO_CORRECT_PROMPT,
    AUTHN_REQUEST_CIE_NO_CORRECT_SCOPE,
    AUTHN_REQUEST_CIE_NO_PROMPT,
    AUTHN_REQUEST_CIE_NO_SCOPE,
    AUTHN_REQUEST_SPID,
    AUTHN_REQUEST_SPID_NO_ACR_VALUES,
    AUTHN_REQUEST_SPID_NO_CLIENT_ID,
    AUTHN_REQUEST_SPID_NO_CODE_CHALLENGE,
    AUTHN_REQUEST_SPID_NO_CODE_CHALLENGE_METHOD,
    AUTHN_REQUEST_SPID_NO_CORRECT_ACR_VALUES,
    AUTHN_REQUEST_SPID_NO_CORRECT_CLAIMS,
    AUTHN_REQUEST_SPID_NO_CORRECT_CODE_CHALLENGE_METHOD,
    AUTHN_REQUEST_SPID_NO_CORRECT_NONCE,
    AUTHN_REQUEST_SPID_NO_CORRECT_PROMPT,
    AUTHN_REQUEST_SPID_NO_CORRECT_REDIRECT_URL,
    AUTHN_REQUEST_SPID_NO_CORRECT_RESPONSE_TYPE,
    AUTHN_REQUEST_SPID_NO_CORRECT_SCOPE,
    AUTHN_REQUEST_SPID_NO_CORRECT_STATE,
    AUTHN_REQUEST_SPID_NO_CORRECT_UI_LOCALES,
    AUTHN_REQUEST_SPID_NO_NONCE,
    AUTHN_REQUEST_SPID_NO_PROMPT,
    AUTHN_REQUEST_SPID_NO_REDIRECT_URL,
    AUTHN_REQUEST_SPID_NO_RESPONSE_TYPE,
    AUTHN_REQUEST_SPID_NO_SCOPE,
    AUTHN_REQUEST_SPID_NO_STATE,
)

logger = logging.getLogger(__name__)


class AuthRequestTest(TestCase):
    def test_validate_spid(self):
        AuthenticationRequestSpid(**AUTHN_REQUEST_SPID)

    def test_validate_spid_no_client_id(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_SPID_NO_CLIENT_ID)

    def test_validate_spid_no_correct_claims(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_SPID_NO_CORRECT_CLAIMS)

    def test_validate_spid_no_code_challenge(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_SPID_NO_CODE_CHALLENGE)

    def test_validate_spid_no_code_challenge_method(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_SPID_NO_CODE_CHALLENGE_METHOD)

    def test_validate_spid_no_correct_code_challenge_method(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(
                **AUTHN_REQUEST_SPID_NO_CORRECT_CODE_CHALLENGE_METHOD
            )

    def test_validate_spid_no_nonce(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_SPID_NO_NONCE)

    def test_validate_spid_no_correct_nonce(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_SPID_NO_CORRECT_NONCE)

    def test_validate_spid_no_prompt(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_SPID_NO_PROMPT)

    def test_validate_spid_no_correct_prompt(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_SPID_NO_CORRECT_PROMPT)

    def test_validate_spid_no_redirect_url(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_SPID_NO_REDIRECT_URL)

    def test_validate_spid_no_correct_redirect_url(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_SPID_NO_CORRECT_REDIRECT_URL)

    def test_validate_spid_no_response_type(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_SPID_NO_RESPONSE_TYPE)

    def test_validate_spid_no_correct_response_type(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_SPID_NO_CORRECT_RESPONSE_TYPE)

    def test_validate_spid_no_scope(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_SPID_NO_SCOPE)

    def test_validate_spid_no_correct_scope(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_SPID_NO_CORRECT_SCOPE)

    def test_validate_spid_no_acr_values(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_SPID_NO_ACR_VALUES)

    def test_validate_spid_no_correct_acr_values(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_SPID_NO_CORRECT_ACR_VALUES)

    def test_validate_spid_no_state(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_SPID_NO_STATE)

    def test_validate_spid_no_correct_state(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_SPID_NO_CORRECT_STATE)

    def test_validate_spid_no_correct_ui_locales(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_SPID_NO_CORRECT_UI_LOCALES)

    def test_validate_cie(self):
        AuthenticationRequestCie(**AUTHN_REQUEST_CIE)

    def test_validate_cie_no_acr_values(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_CIE_NO_ACR_VALUES)

    def test_validate_cie_no_correct_acr_values(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_CIE_NO_CORRECT_ACR_VALUES)

    def test_validate_cie_no_prompt(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_CIE_NO_PROMPT)

    def test_validate_cie_no_correct_prompt(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_CIE_NO_CORRECT_PROMPT)

    def test_validate_cie_no_scope(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_CIE_NO_SCOPE)

    def test_validate_cie_no_correct_scope(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_CIE_NO_CORRECT_SCOPE)
