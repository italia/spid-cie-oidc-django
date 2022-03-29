
from django.test import TestCase
from spid_cie_oidc.provider.models import OidcSession
from spid_cie_oidc.provider.views.__init__ import OpBase


class InitTest(TestCase):

    def setUp(self):            
        self.client_assertion = 'eyJhbGciOiJSUzI1NiIsImtpZCI6IjJIbm9GUzNZbkM5dGppQ2FpdmhXTFZVSjNBeHdHR3pfOTh1UkZhcU1FRXMifQ.eyJpc3MiOiJodHRwOi8vMTI3LjAuMC4xOjgwMDAvb2lkYy9ycC8iLCJzdWIiOiJodHRwOi8vMTI3LjAuMC4xOjgwMDAvb2lkYy9ycC8iLCJhdWQiOlsiaHR0cDovLzEyNy4wLjAuMTo4MDAwL29pZGMvb3AvdG9rZW4vIl0sImlhdCI6MTY0ODQ5NTc1NywiZXhwIjoxNjQ4NDk3NzM3LCJqdGkiOiI0OWE2OGQyMS03NTE1LTRmNDMtODZhZC1hMDNhMWNmNDFmNTgifQ.EaWmmuDhoa8jt_go4zrY5AhTGnljIS1zNwIF-f9eBidAiWPYaKwmXRsRoXrAeybLcJ5E8-7TO1S8jZiCxcElQPdRRvuP9ZsgNhfEqDhZtabkwGBFt4gpQZnFsgGDMAi-v4sTM55VsnIJIMrHPNIckZfL-YhD-FSCtDsqrCkCnucXR58Kfp_SEx3hJvrU-2vcOeNXJBTqs3pHl9jws9GJIf6bZd7vQqTMolCC4zBzUp7yT3OXqMt9uCUhLZzLtpTRW0_-u-KW4h44eHOdEf6ePqiFhjflF9_T6cM-OBqzaK0eVvg6RcasvF3IyxdG-ME5crapAibeePqg_Hy__Q5idQ'
        self.session = OidcSession.objects.create(
            user_uid="",
            nonce="",
            authz_request={"scope": "offline_access", "prompt": "consent", "nonce": "123", "acr_values":["https://www.spid.gov.it/SpidL1"]},
            client_id="",
            auth_code="code",
        )
    
    def test_validate_authz_request_object(self):
        with self.assertRaises(Exception):
            OpBase.validate_authz_request_object(self,{})

    def test_check_client_assertion(self):
        with self.assertRaises(Exception):
            OpBase.check_client_assertion(self, client_id = "", client_assertion = self.client_assertion)

    def test_get_refresh_token(self):
        result = OpBase.get_refresh_token(
            self,
            iss_sub = "sub",
            sub = "sub",
            authz = self.session,
            jwt_at = "jwt_at",
            commons= {}
        )
        self.assertEqual(result["sub"], "sub")
