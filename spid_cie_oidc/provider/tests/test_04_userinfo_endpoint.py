from copy import deepcopy

from django.test import Client, TestCase
from django.urls import reverse
from spid_cie_oidc.accounts.models import User
from spid_cie_oidc.authority.tests.settings import (
    RP_METADATA,
    rp_onboarding_data
)
from spid_cie_oidc.entity.jwtse import create_jws
from spid_cie_oidc.entity.models import (
    FederationEntityConfiguration,
    FetchedEntityStatement, 
    TrustChain
)
from spid_cie_oidc.entity.tests.settings import TA_SUB
from spid_cie_oidc.entity.utils import (
    datetime_from_timestamp,
    exp_from_now,
    iat_now
    )
from spid_cie_oidc.provider.models import IssuedToken, OidcSession
from spid_cie_oidc.provider.tests.settings import op_conf, op_conf_priv_jwk


class UserInfoEndpointTest(TestCase):

    def setUp(self):
        self.RP_SUB = rp_onboarding_data["sub"]
        self.op_local_conf = deepcopy(op_conf)
        FederationEntityConfiguration.objects.create(**self.op_local_conf)
        self.ta_fes = FetchedEntityStatement.objects.create(
            sub=TA_SUB,
            iss=TA_SUB,
            exp=datetime_from_timestamp(exp_from_now(33)),
            iat=datetime_from_timestamp(iat_now()),
        )

    def define_db(self):
        session = OidcSession.objects.create(
            user=User.objects.create(
                username = "username", attributes = {"email" : "test@test.it"}
            ),
            user_uid="",
            nonce="",
            authz_request={
                "scope": "openid", "nonce": "123", "claims":{
                    "userinfo":{"email": None}
                }
            },
            client_id=self.RP_SUB,
        )

        access_token = {
            "iss": self.RP_SUB,
            "sub": op_conf["sub"],
            "aud": [self.RP_SUB],
            "client_id": self.RP_SUB,
            "scope": "openid",
        }
        jwt_at = create_jws(access_token, op_conf_priv_jwk, typ="at+jwt")
        iss_token_data = dict(
            session=session,
            access_token= jwt_at,
            id_token= "id_token",
            expires=datetime_from_timestamp(exp_from_now())
        )
        IssuedToken.objects.create(**iss_token_data)
        headers= {
            "HTTP_AUTHORIZATION": f"Bearer {jwt_at}"
        }
        return headers

    def test_userinfo_endpoint_no_header(self):
        client = Client()
        url = reverse("oidc_provider_userinfo_endpoint")
        res = client.get(url, {})
        self.assertTrue(res.status_code == 403)

    def test_userinfo_endpoint_no_issued_token_session(self):
        client = Client()
        url = reverse("oidc_provider_userinfo_endpoint")
        headers= {
            "HTTP_AUTHORIZATION": "Bearer dC34Pf6kdG"
        }
        res = client.get(url, data  = {}, **headers)
        self.assertTrue(res.status_code == 403)

    def test_userinfo_endpoint_no_tc(self):
        headers = self.define_db()
        client = Client()
        url = reverse("oidc_provider_userinfo_endpoint")
        res = client.get(url, data  = {}, **headers)
        self.assertTrue(res.status_code == 403)

    def test_userinfo_endpoint_ok(self):
        headers = self.define_db()
        self.trust_chain = TrustChain.objects.create(
            sub=self.RP_SUB,
            exp=datetime_from_timestamp(exp_from_now(33)),
            jwks = [],
            metadata=RP_METADATA,
            status="valid",
            trust_anchor=self.ta_fes,
            is_active=True,
        )
        client = Client()
        url = reverse("oidc_provider_userinfo_endpoint")
        res = client.get(url, data  = {}, **headers)
        self.assertTrue(res.status_code == 200)

