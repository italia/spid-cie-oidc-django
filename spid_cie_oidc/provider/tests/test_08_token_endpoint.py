from copy import deepcopy

from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from spid_cie_oidc.accounts.models import User
from spid_cie_oidc.authority.tests.settings import (
    RP_METADATA,
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
from spid_cie_oidc.relying_party.utils import get_pkce


RP_SUB = rp_conf["sub"]
RP_CLIENT_ID = rp_conf["metadata"]["openid_relying_party"]["client_id"]
PKCE = get_pkce()

class RefreshTokenTest(TestCase):

    def setUp(self): 
        self.op_local_conf = deepcopy(op_conf)
        FederationEntityConfiguration.objects.create(**self.op_local_conf)
        self.ta_fes = FetchedEntityStatement.objects.create(
            sub=TA_SUB,
            iss=TA_SUB,
            exp=datetime_from_timestamp(exp_from_now(33)),
            iat=datetime_from_timestamp(iat_now()),
        )
        self.trust_chain = TrustChain.objects.create(
            sub=RP_SUB,
            exp=datetime_from_timestamp(exp_from_now(33)),
            jwks = [],
            metadata=RP_METADATA,
            status="valid",
            trust_anchor=self.ta_fes,
            is_active=True,
        )
        self.jwt_auds = [op_conf["sub"], "http://testserver/oidc/op/", "http://testserver/oidc/op/token/"]
        CLIENT_ASSERTION = {
            "iss": RP_SUB,
            "sub": RP_SUB,
            "aud": self.jwt_auds,
            "exp": exp_from_now(),
            "iat": iat_now(),
            "jti": "jti",
        }
        self.ca_jws = create_jws(CLIENT_ASSERTION, RP_METADATA_JWK1)
        
        self.refresh_token = {
            "iss": self.op_local_conf["sub"],
            "sub": RP_SUB,
            "exp": exp_from_now(),
            "iat": iat_now(),
            "aud": self.jwt_auds,
            "client_id": RP_CLIENT_ID,
            "scope": "openid",
        }
        session = OidcSession.objects.create(
            user=User.objects.create(username = "username"),
            user_uid="",
            nonce="",
            authz_request={"scope": "openid", "nonce": "123", "code_challenge": PKCE["code_challenge"]}, 
            client_id="",
            auth_code="code",
        )
        IssuedToken.objects.create(
            access_token = create_jws(self.refresh_token, op_conf_priv_jwk, typ="at-jwt"),
            refresh_token = create_jws(self.refresh_token, op_conf_priv_jwk),
            session = session,
            expires = timezone.localtime()
        )

    def test_token_endpoint(self):
        client = Client()
        url = reverse("oidc_provider_token_endpoint")
        
        request = dict(
            client_id = RP_CLIENT_ID,
            client_assertion = self.ca_jws,
            client_assertion_type = "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            grant_type="authorization_code",
            code="code",
            code_verifier = PKCE["code_verifier"]
        )
        res = client.post(url, request)
        self.assertTrue(res.status_code == 200)
        self.assertTrue(res.json().get("access_token"))

    def test_token_endpoint_get(self):
        client = Client()
        url = reverse("oidc_provider_token_endpoint")
        request = dict(
            client_id = RP_CLIENT_ID,
            client_assertion = self.ca_jws,
            client_assertion_type = "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            grant_type="authorization_code",
            code = "code",
            code_verifier = "code_verifier"
        )
        res = client.get(url, request)
        self.assertTrue(res.status_code == 400)

    def test_token_endpoint_no_client_id(self):
        client = Client()
        url = reverse("oidc_provider_token_endpoint")
        request = dict(
            client_assertion = self.ca_jws,
            client_assertion_type = "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            grant_type="authorization_code",
            code = "code",
            code_verifier = "code_verifier"
        )
        res = client.post(url, request)
        self.assertTrue(res.status_code == 400)
        self.assertTrue("invalid_request" == res.json().get("error"))

    def test_token_endpoint_no_session(self):
        OidcSession.objects.all().delete()
        client = Client()
        url = reverse("oidc_provider_token_endpoint")
        request = dict(
            client_id = RP_CLIENT_ID,
            client_assertion = self.ca_jws,
            client_assertion_type = "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            grant_type="authorization_code",
            code = "code",
            code_verifier = "code_verifier"
        )
        res = client.post(url, request)
        self.assertTrue(res.status_code == 400)
