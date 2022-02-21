import logging

from django.test import TestCase
from spid_cie_oidc.onboarding.validators.token_request import (
    TokenAuthnCodeRequest,
    TokenRefreshRequest,
)

from .token_request_settings import TOKEN_AUTHN_CODE_REQUEST, TOKEN_REFRESH_REQUEST

logger = logging.getLogger(__name__)


class TokenRequestTest(TestCase):
    def test_validate_request(self):
        TokenAuthnCodeRequest(**TOKEN_AUTHN_CODE_REQUEST)

    def test_validate_refresh_request(self):
        TokenRefreshRequest(**TOKEN_REFRESH_REQUEST)
