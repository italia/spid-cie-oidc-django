
from copy import deepcopy

from django.test import Client, TestCase
from django.urls import reverse
from spid_cie_oidc.accounts.models import User
from spid_cie_oidc.authority.tests.settings import (
    RP_CONF_AS_JSON,                          
    RP_METADATA_JWK1,
    rp_conf
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

RP_SUB = rp_conf["sub"]
RP_CLIENT_ID = rp_conf["metadata"]["openid_relying_party"]["client_id"]

class RevocationEndponitTest(TestCase):

    def setUp(self): 
        ta_fes = FetchedEntityStatement.objects.create(
            sub=TA_SUB,
            iss=TA_SUB,
            exp=datetime_from_timestamp(exp_from_now(33)),
            iat=datetime_from_timestamp(iat_now()),
        )
        self.op_local_conf = deepcopy(op_conf)
        FederationEntityConfiguration.objects.create(**self.op_local_conf)
        self.jwt_auds = [op_conf["sub"], "http://testserver/oidc/op/", "http://testserver/oidc/op/revocation/"]
        CLIENT_ASSERTION = {
            "iss": RP_SUB,
            "sub": RP_SUB,
            "aud": self.jwt_auds,
            "exp": exp_from_now(),
            "iat": iat_now(),
            "jti": "jti",
        }
        self.ca_jws = create_jws(CLIENT_ASSERTION, RP_METADATA_JWK1)
        access_token = {
            "iss": self.op_local_conf["sub"],
            "sub": RP_SUB,
            "aud": self.jwt_auds,
            "client_id": RP_CLIENT_ID,
            "scope": "openid",
        }
        self.at_jws = create_jws(access_token, op_conf_priv_jwk)
        self.request = dict(
            client_id = RP_CLIENT_ID,
            client_assertion = self.ca_jws,
            client_assertion_type = "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            token = self.at_jws,
        )   
        session = OidcSession.objects.create(
            user=User.objects.create(username = "username"),
            user_uid="",
            nonce="",
            authz_request={"scope": "openid"},
            client_id=rp_conf["sub"],
        )
        iss_token_data = dict(
            session=session,
            access_token= self.at_jws,
            id_token= "id_token",
            refresh_token= "refresh_token",
            expires=datetime_from_timestamp(exp_from_now())
        )
        IssuedToken.objects.create(**iss_token_data)

        TrustChain.objects.create(
            sub=RP_CONF_AS_JSON["sub"],
            exp=datetime_from_timestamp(exp_from_now(33)),
            jwks = [],
            metadata=RP_CONF_AS_JSON["metadata"],
            status="valid",
            trust_anchor=ta_fes,
            is_active=True,
        )

    def test_revocation_endpoint(self):
        client = Client()
        url = reverse("oidc_provider_end_session_endpoint")
        res = client.post(url, self.request)
        self.assertTrue(res.status_code == 200)

    def test_revocation_endpoint_no_correct_client_assert(self):
        client = Client()
        request = deepcopy(self.request)
        request["client_assertion"] = "q.q.q"
        url = reverse("oidc_provider_end_session_endpoint")
        res = client.post(url, request)
        self.assertTrue(res.status_code == 400)

    def test_revocation_endpoint_no_issued_token(self):
        client = Client()
        IssuedToken.objects.all().delete()
        url = reverse("oidc_provider_end_session_endpoint")
        res = client.post(url, self.request)
        self.assertTrue(res.status_code == 400)
