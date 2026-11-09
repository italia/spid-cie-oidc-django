
from django.test import TestCase, override_settings
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

    def test_scope_releases_profile_and_email_claims(self):
        view = OpBase()
        attributes = {
            "username": "ada",
            "given_name": "Ada",
            "family_name": "Lovelace",
            "birthdate": "1815-12-10",
            "fiscal_number": "TINIT-ADA",
            "email": "ada@example.it",
            "email_verified": True,
        }
        authz_request = {"scope": "openid profile email"}
        released = view.claims_released_by_scope(authz_request, attributes)
        self.assertEqual(released["given_name"], "Ada")
        self.assertEqual(released["family_name"], "Lovelace")
        self.assertEqual(released["birthdate"], "1815-12-10")
        self.assertEqual(released["username"], "ada")
        self.assertEqual(
            released["https://attributes.eid.gov.it/fiscal_number"],
            "TINIT-ADA",
        )
        self.assertEqual(released["email"], "ada@example.it")
        self.assertIs(released["email_verified"], True)

        as_list = view.claims_released_by_scope(
            {"scope": ["openid", "profile"]},
            attributes,
        )
        self.assertEqual(as_list["given_name"], "Ada")
        self.assertNotIn("email", as_list)

    @override_settings(OIDCFED_DEFAULT_PROVIDER_PROFILE="cie")
    def test_cie_id_token_includes_profile_scope(self):
        view = OpBase()

        class Authz:
            authz_request = {"scope": "openid profile email", "nonce": "n"}
            user = type("User", (), {})()

        Authz.user.attributes = {
            "given_name": "Ada",
            "family_name": "Lovelace",
            "birthdate": "1815-12-10",
            "username": "ada",
            "fiscal_number": "TINIT-ADA",
            "email": "ada@example.it",
            "email_verified": False,
        }
        claims = view.get_id_token_claims(Authz())
        self.assertEqual(claims["given_name"], "Ada")
        self.assertEqual(claims["family_name"], "Lovelace")
        self.assertEqual(claims["birthdate"], "1815-12-10")
        self.assertEqual(claims["email"], "ada@example.it")
        self.assertIs(claims["email_verified"], False)
        self.assertNotIn("username", claims)

    def test_spid_id_token_does_not_take_scope_attributes(self):
        view = OpBase()

        class Authz:
            authz_request = {"scope": "openid profile"}
            user = type("User", (), {"attributes": {"given_name": "Ada"}})()

        self.assertEqual(view.get_id_token_claims(Authz()), {})

    def test_client_organization_name_fallback_order(self):
        class TrustChain:
            def __init__(self, metadata):
                self.metadata = metadata

        view = OpBase()
        view.payload = {"client_id": "https://rp.example/oidc"}
        full = {
            "federation_entity": {
                "federation_fetch_endpoint": "https://rp.example/fetch",
                "organization_name": "Federation Org",
            },
            "openid_relying_party": {
                "organization_name": "RP Org",
                "client_name": "RP Client",
                "client_id": "https://rp.example/oidc",
            },
        }
        self.assertEqual(
            view.get_client_organization_name(TrustChain(full)),
            "Federation Org",
        )

        no_federation_name = {
            "federation_entity": {
                "federation_fetch_endpoint": "https://rp.example/fetch",
            },
            "openid_relying_party": {
                "organization_name": "RP Org",
                "client_name": "RP Client",
                "client_id": "https://rp.example/oidc",
            },
        }
        self.assertEqual(
            view.get_client_organization_name(TrustChain(no_federation_name)),
            "RP Org",
        )

        client_name_only = {
            "federation_entity": {
                "federation_fetch_endpoint": "https://rp.example/fetch",
            },
            "openid_relying_party": {
                "client_name": "RP Client",
                "client_id": "https://rp.example/oidc",
            },
        }
        self.assertEqual(
            view.get_client_organization_name(TrustChain(client_name_only)),
            "RP Client",
        )

        client_id_only = {
            "federation_entity": {"contacts": ["ops@rp.example"]},
            "openid_relying_party": {"client_id": "https://rp.example/oidc"},
        }
        self.assertEqual(
            view.get_client_organization_name(TrustChain(client_id_only)),
            "https://rp.example/oidc",
        )

        self.assertEqual(
            view.get_client_organization_name(TrustChain({})),
            "https://rp.example/oidc",
        )
        self.assertEqual(view.get_client_organization_name(None), "https://rp.example/oidc")
