from copy import deepcopy

from django.test import Client, TestCase
from django.urls import reverse
from spid_cie_oidc.accounts.models import User
from spid_cie_oidc.authority.tests.settings import (
    RP_METADATA, 
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
from spid_cie_oidc.provider.tests.settings import (
    op_conf, 
    op_conf_priv_jwk
)


class IntrospectionEndpointTest(TestCase):

    def setUp(self):
        self.RP_SUB = rp_conf["sub"]
        self.RP_CLIENT_ID = rp_conf["metadata"]["openid_relying_party"]["client_id"]
        self.jwt_auds = [op_conf["sub"], "http://testserver/oidc/op/", "http://testserver/oidc/op/introspection/"]
        CLIENT_ASSERTION = {
            "iss": self.RP_SUB,
            "sub": self.RP_SUB,
            "aud": self.jwt_auds,
            "exp": exp_from_now(),
            "iat": iat_now(),
            "jti": "jti",
        }
        self.ca_jws = create_jws(CLIENT_ASSERTION, rp_conf["jwks_core"][0])
        token = {
            "iss": self.RP_SUB,
            "sub": op_conf["sub"],
            "aud": self.jwt_auds,
            "client_id": self.RP_SUB,
            "scope": "openid",
        }
        self.jwt_token = create_jws(token, op_conf_priv_jwk, typ="at+jwt")  
        session = OidcSession.objects.create(
            user=User.objects.create(username = "username"),
            user_uid="",
            nonce="",
            authz_request={"scope": "openid"},
            client_id=self.RP_SUB,
        )
        iss_token_data = dict(
            session=session,
            access_token= self.jwt_token,
            id_token= "id_token",
            refresh_token= "refresh_token",
            expires=datetime_from_timestamp(exp_from_now())
        )
        IssuedToken.objects.create(**iss_token_data)
        self.op_local_conf = deepcopy(op_conf)
        FederationEntityConfiguration.objects.create(**self.op_local_conf)
        self.ta_fes = FetchedEntityStatement.objects.create(
            sub=TA_SUB,
            iss=TA_SUB,
            exp=datetime_from_timestamp(exp_from_now(33)),
            iat=datetime_from_timestamp(iat_now()),
        )
        self.trust_chain = TrustChain.objects.create(
            sub=self.RP_SUB,
            exp=datetime_from_timestamp(exp_from_now(33)),
            jwks = [],
            metadata=RP_METADATA,
            status="valid",
            trust_anchor=self.ta_fes,
            is_active=True,
        )

    def test_introspection_endpoint(self):
        client = Client()
        url = reverse("oidc_provider_introspection_endpoint")
        request = {
            "client_assertion" : self.ca_jws,
            "client_assertion_type" : "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_id" : self.RP_SUB,
            "token" : self.jwt_token

        }
        
        res = client.post(url, request)
        self.assertTrue(res.status_code == 200)
        self.assertTrue("openid" in res.content.decode())

    def test_introspection_endpoint_get(self):
        client = Client()
        url = reverse("oidc_provider_introspection_endpoint")
        request = {
            "client_assertion" : self.ca_jws,
            "client_assertion_type" : "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_id" : self.RP_SUB,
            "token" : self.jwt_token

        }
        res = client.get(url, request)
        self.assertTrue(res.status_code == 400)

    def test_introspection_endpoint_validation_error(self):
        client = Client()
        url = reverse("oidc_provider_introspection_endpoint")
        request = {
            "client_assertion" : self.ca_jws,
            "client_assertion_type" : "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "token" : self.jwt_token

        }
        res = client.post(url, request)
        self.assertTrue(res.status_code == 400)
        self.assertTrue(res.json()["error"] == "invalid_request")
