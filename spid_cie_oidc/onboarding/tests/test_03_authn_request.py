from django.test import TestCase
from spid_cie_oidc.onboarding.validators.authn_requests import AuthenticationRequestSpid, AuthenticationRequestCie, validate_message
from . authn_request_settings import AUTHN_REQUEST_SPID, AUTHN_REQUEST_CIE
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)

class AuthRequestTest(TestCase):

    def test_authn_1 (self):

        def validate_spid():
            try:
                AuthenticationRequestSpid(**AUTHN_REQUEST_SPID)
                validate_message(AUTHN_REQUEST_SPID, AuthenticationRequestSpid.get_claims())
                logger.info("ATUHN REQUEST SPID CHECK PASSED")
            except ValidationError as e:
                logger.info("CHECK ATUHN REQUEST SPID FAILED, SEE ERRORS:")
                logger.info(e.json())
        
        def validate_cie():
            try:
                AuthenticationRequestCie(**AUTHN_REQUEST_CIE)
                validate_message(AUTHN_REQUEST_CIE, AuthenticationRequestCie.get_claims())
                logger.info("ATUHN REQUEST CIE CHECK PASSED")
            except ValidationError as e:
                logger.info("CHECK ATUHN REQUEST CIE FAILED, SEE ERRORS:")
                logger.info(e.json())

        logger.info(AuthenticationRequestSpid.schema_json(indent=2))
        validate_spid()
        #logger.info(AuthenticationRequestCie.schema_json(indent=2))
        validate_cie()
        

        
