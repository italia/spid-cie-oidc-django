import logging

from django.test import TestCase
from pydantic import ValidationError
from spid_cie_oidc.onboarding.validators.authn_requests import (
    AuthenticationRequestCie, AuthenticationRequestSpid, validate_message)

from .authn_request_settings import (
    AUTHN_REQUEST_CIE, AUTHN_REQUEST_CIE_NO_ACR_VALUES,
    AUTHN_REQUEST_CIE_NO_CORRECT_ACR_VALUES,
    AUTHN_REQUEST_CIE_NO_CORRECT_PROMPT, AUTHN_REQUEST_CIE_NO_CORRECT_SCOPE,
    AUTHN_REQUEST_CIE_NO_PROMPT, AUTHN_REQUEST_CIE_NO_SCOPE,
    AUTHN_REQUEST_SPID, AUTHN_REQUEST_SPID_NO_ACR_VALUES,
    AUTHN_REQUEST_SPID_NO_CLIENT_ID, AUTHN_REQUEST_SPID_NO_CODE_CHALLENGE,
    AUTHN_REQUEST_SPID_NO_CODE_CHALLENGE_METHOD,
    AUTHN_REQUEST_SPID_NO_CORRECT_ACR_VALUES,
    AUTHN_REQUEST_SPID_NO_CORRECT_CLAIMS,
    AUTHN_REQUEST_SPID_NO_CORRECT_CODE_CHALLENGE_METHOD,
    AUTHN_REQUEST_SPID_NO_CORRECT_NONCE, AUTHN_REQUEST_SPID_NO_CORRECT_PROMPT,
    AUTHN_REQUEST_SPID_NO_CORRECT_REDIRECT_URL,
    AUTHN_REQUEST_SPID_NO_CORRECT_RESPONSE_TYPE,
    AUTHN_REQUEST_SPID_NO_CORRECT_SCOPE, AUTHN_REQUEST_SPID_NO_CORRECT_STATE,
    AUTHN_REQUEST_SPID_NO_CORRECT_UI_LOCALES, AUTHN_REQUEST_SPID_NO_NONCE,
    AUTHN_REQUEST_SPID_NO_PROMPT, AUTHN_REQUEST_SPID_NO_REDIRECT_URL,
    AUTHN_REQUEST_SPID_NO_RESPONSE_TYPE, AUTHN_REQUEST_SPID_NO_SCOPE,
    AUTHN_REQUEST_SPID_NO_STATE)

logger = logging.getLogger(__name__)

class AuthRequestTest(TestCase):

    def test_validate_spid(self):
        AuthenticationRequestSpid(**AUTHN_REQUEST_SPID)
        validate_message(AUTHN_REQUEST_SPID, AuthenticationRequestSpid.get_claims())

    def test_validate_spid_no_client_id(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_SPID_NO_CLIENT_ID) 
            validate_message(AUTHN_REQUEST_SPID_NO_CLIENT_ID, AuthenticationRequestSpid.get_claims())

    def test_validate_spid_no_correct_claims(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_SPID_NO_CORRECT_CLAIMS) 
            validate_message(AUTHN_REQUEST_SPID_NO_CORRECT_CLAIMS, AuthenticationRequestSpid.get_claims())
    
    def test_validate_spid_no_code_challenge(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_SPID_NO_CODE_CHALLENGE) 
            validate_message(AUTHN_REQUEST_SPID_NO_CODE_CHALLENGE, AuthenticationRequestSpid.get_claims())

    def test_validate_spid_no_code_challenge_method(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_SPID_NO_CODE_CHALLENGE_METHOD) 
            validate_message(AUTHN_REQUEST_SPID_NO_CODE_CHALLENGE_METHOD, AuthenticationRequestSpid.get_claims())

    def test_validate_spid_no_correct_code_challenge_method(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_SPID_NO_CORRECT_CODE_CHALLENGE_METHOD) 
            validate_message(AUTHN_REQUEST_SPID_NO_CORRECT_CODE_CHALLENGE_METHOD, AuthenticationRequestSpid.get_claims())

    def test_validate_spid_no_nonce(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_SPID_NO_NONCE) 
            validate_message(AUTHN_REQUEST_SPID_NO_NONCE, AuthenticationRequestSpid.get_claims())

    def test_validate_spid_no_correct_nonce(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_SPID_NO_CORRECT_NONCE) 
            validate_message(AUTHN_REQUEST_SPID_NO_CORRECT_NONCE, AuthenticationRequestSpid.get_claims())

    def test_validate_spid_no_prompt(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_SPID_NO_PROMPT) 
            validate_message(AUTHN_REQUEST_SPID_NO_PROMPT, AuthenticationRequestSpid.get_claims())

    def test_validate_spid_no_correct_prompt(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_SPID_NO_CORRECT_PROMPT) 
            validate_message(AUTHN_REQUEST_SPID_NO_CORRECT_PROMPT, AuthenticationRequestSpid.get_claims())

    def test_validate_spid_no_redirect_url(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_SPID_NO_REDIRECT_URL) 
            validate_message(AUTHN_REQUEST_SPID_NO_REDIRECT_URL, AuthenticationRequestSpid.get_claims())

    def test_validate_spid_no_correct_redirect_url(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_SPID_NO_CORRECT_REDIRECT_URL) 
            validate_message(AUTHN_REQUEST_SPID_NO_CORRECT_REDIRECT_URL, AuthenticationRequestSpid.get_claims())

    def test_validate_spid_no_response_type(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_SPID_NO_RESPONSE_TYPE) 
            validate_message(AUTHN_REQUEST_SPID_NO_RESPONSE_TYPE, AuthenticationRequestSpid.get_claims())

    def test_validate_spid_no_correct_response_type(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_SPID_NO_CORRECT_RESPONSE_TYPE) 
            validate_message(AUTHN_REQUEST_SPID_NO_CORRECT_RESPONSE_TYPE, AuthenticationRequestSpid.get_claims())

    def test_validate_spid_no_scope(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_SPID_NO_SCOPE) 
            validate_message(AUTHN_REQUEST_SPID_NO_SCOPE, AuthenticationRequestSpid.get_claims())

    def test_validate_spid_no_correct_scope(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_SPID_NO_CORRECT_SCOPE) 
            validate_message(AUTHN_REQUEST_SPID_NO_CORRECT_SCOPE, AuthenticationRequestSpid.get_claims())

    def test_validate_spid_no_acr_values(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_SPID_NO_ACR_VALUES) 
            validate_message(AUTHN_REQUEST_SPID_NO_ACR_VALUES, AuthenticationRequestSpid.get_claims())

    def test_validate_spid_no_correct_acr_values(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_SPID_NO_CORRECT_ACR_VALUES) 
            validate_message(AUTHN_REQUEST_SPID_NO_CORRECT_ACR_VALUES, AuthenticationRequestSpid.get_claims())

    def test_validate_spid_no_state(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_SPID_NO_STATE) 
            validate_message(AUTHN_REQUEST_SPID_NO_STATE, AuthenticationRequestSpid.get_claims())

    def test_validate_spid_no_correct_state(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_SPID_NO_CORRECT_STATE) 
            validate_message(AUTHN_REQUEST_SPID_NO_CORRECT_STATE, AuthenticationRequestSpid.get_claims())

    def test_validate_spid_no_correct_ui_locales(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_SPID_NO_CORRECT_UI_LOCALES) 
            validate_message(AUTHN_REQUEST_SPID_NO_CORRECT_UI_LOCALES, AuthenticationRequestSpid.get_claims())

    def test_validate_cie(self):
        AuthenticationRequestCie(**AUTHN_REQUEST_CIE)
        validate_message(AUTHN_REQUEST_CIE, AuthenticationRequestCie.get_claims())
        
    def test_validate_cie_no_acr_values(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_CIE_NO_ACR_VALUES) 
            validate_message(AUTHN_REQUEST_CIE_NO_ACR_VALUES, AuthenticationRequestSpid.get_claims())

    def test_validate_cie_no_correct_acr_values(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_CIE_NO_CORRECT_ACR_VALUES) 
            validate_message(AUTHN_REQUEST_CIE_NO_CORRECT_ACR_VALUES, AuthenticationRequestSpid.get_claims())

    def test_validate_cie_no_prompt(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_CIE_NO_PROMPT) 
            validate_message(AUTHN_REQUEST_CIE_NO_PROMPT, AuthenticationRequestSpid.get_claims())

    def test_validate_cie_no_correct_prompt(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_CIE_NO_CORRECT_PROMPT) 
            validate_message(AUTHN_REQUEST_CIE_NO_CORRECT_PROMPT, AuthenticationRequestSpid.get_claims())

    def test_validate_cie_no_scope(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_CIE_NO_SCOPE) 
            validate_message(AUTHN_REQUEST_CIE_NO_SCOPE, AuthenticationRequestSpid.get_claims())

    def test_validate_cie_no_correct_scope(self):
        with self.assertRaises(ValidationError):
            AuthenticationRequestSpid(**AUTHN_REQUEST_CIE_NO_CORRECT_SCOPE) 
            validate_message(AUTHN_REQUEST_CIE_NO_CORRECT_SCOPE, AuthenticationRequestSpid.get_claims())
