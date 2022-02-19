import logging

from django.test import TestCase
from pydantic import ValidationError
from spid_cie_oidc.onboarding.validators.token_request import (
    TokenAuthnCodeRequest, TokenRefreshRequest)

from .authn_request_settings import (TOKEN_AUTHN_CODE_REQUEST,
                                     TOKEN_REFRESH_REQUEST)

logger = logging.getLogger(__name__)

class TokenRequestTest(TestCase):

    def test_validate_request(self):
        TokenAuthnCodeRequest(**TOKEN_AUTHN_CODE_REQUEST)
     
    
    def test_validate_refresh_request(self):
        TokenRefreshRequest(**TOKEN_REFRESH_REQUEST)
     

# logger.info(TokenAuthnCodeRequest.schema_json(indent=2))
# logger.info(TokenRefreshRequest.schema_json(indent=2))
        

        
