import logging

from django.test import TestCase
from pydantic import ValidationError
from spid_cie_oidc.onboarding.validators.authn_response import (
    AuthenticationErrorResponse, AuthenticationErrorResponseCie,
    AuthenticationResponse, AuthenticationResponseCie)

from .authn_request_settings import (AUTHN_ERROR_RESPONSE_CIE,
                                     AUTHN_ERROR_RESPONSE_SPID,
                                     AUTHN_RESPONSE_CIE, AUTHN_RESPONSE_SPID)

logger = logging.getLogger(__name__)

class AuthResponseTest(TestCase):

    def test_validate_response_spid(self):
        AuthenticationResponse(**AUTHN_RESPONSE_SPID)
       
    def test_validate_response_cie(self):
        AuthenticationResponseCie(**AUTHN_RESPONSE_CIE)
        
    def test_validate_error_response_spid(self):
        AuthenticationErrorResponse(**AUTHN_ERROR_RESPONSE_SPID)

    def test_validate_error_response_cie(self):
        AuthenticationErrorResponseCie(**AUTHN_ERROR_RESPONSE_CIE)
        
    
# logger.info(AuthenticationResponse.schema_json(indent=2))
# logger.info(AuthenticationResponseCie.schema_json(indent=2))
# logger.info(AuthenticationErrorResponse.schema_json(indent=2))
# logger.info(AuthenticationErrorResponseCie.schema_json(indent=2))
