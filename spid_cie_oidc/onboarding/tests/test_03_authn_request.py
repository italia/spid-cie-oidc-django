from django.test import TestCase
from spid_cie_oidc.onboarding.authn_requests.schemas import *
from . authn_request_settings import AUTHN_REQUEST_SPID

class AuthRequestTest(TestCase):

    def test_authn_1 (self):
        print(AuthenticationRequest.schema_json(indent=2))
        try:
            AuthenticationRequest(**AUTHN_REQUEST_SPID)
            validate_message(AUTHN_REQUEST_SPID)
            print("CHECK PASSED")
        except ValidationError as e:
            print("CHECK FAILED, SEE ERRORS:")
            print(e.json())