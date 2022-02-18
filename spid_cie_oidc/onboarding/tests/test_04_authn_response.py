from multiprocessing import AuthenticationError
from django.test import TestCase
from spid_cie_oidc.onboarding.validators.authn_response import AuthenticationResponse, AuthenticationResponseCie, AuthenticationErrorResponse, AuthenticationErrorResponseCie
from . authn_request_settings import AUTHN_ERROR_RESPONSE_SPID, AUTHN_RESPONSE_SPID, AUTHN_RESPONSE_CIE, AUTHN_ERROR_RESPONSE_CIE
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)

class AuthResponseTest(TestCase):

    def test_authn_1 (self):

        def validate_response_spid():
            try:
                AuthenticationResponse(**AUTHN_RESPONSE_SPID)
                logger.info("ATUHN RESPONSE SPID CHECK PASSED")
            except ValidationError as e:
                logger.info("CHECK ATUHN RESPONSE SPID FAILED, SEE ERRORS:")
                logger.info(e.json())

        def validate_response_cie():
            try:
                AuthenticationResponseCie(**AUTHN_RESPONSE_CIE)
                logger.info("ATUHN RESPONSE CIE CHECK PASSED")
            except ValidationError as e:
                logger.info("CHECK ATUHN RESPONSE CIE FAILED, SEE ERRORS:")
                logger.info(e.json())

        def validate_error_response_spid():
            try:
                AuthenticationErrorResponse(**AUTHN_ERROR_RESPONSE_SPID)
                logger.info("ATUHN ERROR RESPONSE SPID CHECK PASSED")
            except ValidationError as e:
                logger.info("CHECK ATUHN ERROR RESPONSE SPID FAILED, SEE ERRORS:")
                logger.info(e.json())

        def validate_error_response_cie():
            try:
                AuthenticationErrorResponseCie(**AUTHN_ERROR_RESPONSE_CIE)
                logger.info("ATUHN ERROR RESPONSE CIE CHECK PASSED")
            except ValidationError as e:
                logger.info("CHECK ATUHN ERROR RESPONSE CIE FAILED, SEE ERRORS:")
                logger.info(e.json())
        
    
        logger.info(AuthenticationResponse.schema_json(indent=2))
        logger.info(AuthenticationResponseCie.schema_json(indent=2))
        logger.info(AuthenticationErrorResponse.schema_json(indent=2))
        logger.info(AuthenticationErrorResponseCie.schema_json(indent=2))
        validate_response_spid()
        validate_response_cie()
        validate_error_response_spid()
        validate_error_response_cie()
