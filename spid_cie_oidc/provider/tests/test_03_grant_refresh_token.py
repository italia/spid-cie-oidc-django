

from django.test import TestCase
from spid_cie_oidc.provider.models import IssuedToken, OidcSession
from spid_cie_oidc.authority.tests.settings import  rp_onboarding_data
from spid_cie_oidc.provider.tests.settings import op_conf
from spid_cie_oidc.authority.tests.settings import rp_conf
from spid_cie_oidc.entity.jwtse import create_jws
from spid_cie_oidc.provider.views import grant_refresh_token

RP_SUB = rp_onboarding_data["sub"]

class GrantRefreshToken(TestCase):


    def setUp(self): 
        refresh_token = {
            "iss": op_conf["sub"],
            "sub": RP_SUB,
            "aud": [rp_conf["metadata"]["openid_relying_party"]["client_id"]],
            "client_id": rp_conf["metadata"]["openid_relying_party"]["client_id"],
            "scope": "openid",
        }
        refresh_token.update(self.commons)
        jwt_rt = create_jws(refresh_token, self.issuer.jwks[0], typ="at+jwt")
        session = OidcSession.objects.create(
            user="",
            user_uid="",
            nonce="",
            authz_request={},
            client_id="",
            auth_code="",
        )
        IssuedToken.objects.create(
            refresh_token = refresh_token,
            session = session
        )

    def test_grant_refresh_token(self):
        grant_refresh_token()
        pass