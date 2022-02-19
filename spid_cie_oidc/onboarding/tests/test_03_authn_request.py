import logging

from django.test import TestCase
from pydantic import ValidationError
from spid_cie_oidc.onboarding.validators.authn_requests import (
    AuthenticationRequestCie, AuthenticationRequestSpid, validate_message)

from .authn_request_settings import (AUTHN_REQUEST_CIE, AUTHN_REQUEST_SPID,
                                     AUTHN_REQUEST_SPID_NO_CLIENT_ID,
                                     AUTHN_REQUEST_SPID_NO_CORRECT_CLAIMS)

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
    
    def test_validate_cie(self):
        AuthenticationRequestCie(**AUTHN_REQUEST_CIE)
        validate_message(AUTHN_REQUEST_CIE, AuthenticationRequestCie.get_claims())
        