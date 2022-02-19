from django.test import TestCase
from spid_cie_oidc.onboarding.validators.token_request import TokenAuthnCodeRequest, TokenRefreshRequest
from . authn_request_settings import TOKEN_AUTHN_CODE_REQUEST, TOKEN_REFRESH_REQUEST
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)

class TokenRequestTest(TestCase):

    def test_authn_1 (self):

        def validate_request():
            try:
                TokenAuthnCodeRequest(**TOKEN_AUTHN_CODE_REQUEST)
                logger.info("TOKEN REQUEST CHECK PASSED")
            except ValidationError as e:
                logger.info("CHECK TOKEN REQUEST FAILED, SEE ERRORS:")
                logger.info(e.json())
        
        def validate_refresh_request():
            try:
                TokenRefreshRequest(**TOKEN_REFRESH_REQUEST)
                logger.info("TOKEN REFRESH REQUEST CHECK PASSED")
            except ValidationError as e:
                logger.info("CHECK TOKEN REFRESH REQUEST FAILED, SEE ERRORS:")
                logger.info(e.json())


        logger.info(TokenAuthnCodeRequest.schema_json(indent=2))
        logger.info(TokenRefreshRequest.schema_json(indent=2))
        validate_request()
        validate_refresh_request()
        

        
