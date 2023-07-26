from copy import deepcopy
import time
from cryptojwt.jws.utils import left_hash
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from spid_cie_oidc.accounts.models import User
from spid_cie_oidc.authority.tests.settings import (
    RP_METADATA,
    RP_METADATA_JWK1,
    rp_conf
)
from spid_cie_oidc.entity.jwtse import create_jws, verify_jws
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
            jwks=[],
            metadata=RP_METADATA,
            status="valid",
            trust_anchor=self.ta_fes,
            is_active=True,
        )
        self.jwt_auds = [op_conf["sub"], "http://testserver/oidc/op/", "http://testserver/oidc/op/token"]
        CLIENT_ASSERTION = {
            "iss": RP_SUB,
            "sub": RP_SUB,
            "aud": self.jwt_auds,
            "exp": exp_from_now(),
            "iat": iat_now(),
            "jti": "jti",
        }
        self.ca_jws = create_jws(CLIENT_ASSERTION, RP_METADATA_JWK1)
        refresh_token = {
            "iss": self.op_local_conf["sub"],
            "sub": RP_SUB,
            "aud": self.jwt_auds,
            "client_id": RP_CLIENT_ID,
            "scope": "openid",
        }
        self.rt_jws = create_jws(refresh_token, op_conf_priv_jwk)
        id_token = {
            'sub': '2ed008b45e66ce53e48273dca5a4463bc8ebd036ebaa824f4582627683c2451b',
            'nonce': 'ljbvL3rpscgS4ZGda7cgibXHr7vrNREW',
            'at_hash': '',
            'c_hash': 'tij0h-zL_bSrsVXy-d3qHw',
            'aud': [rp_conf["metadata"]["openid_relying_party"]["client_id"], ],
            'iss': op_conf["sub"],
            'jti': '402e61bd-950c-4934-83d4-c09a05468828',
            'exp': exp_from_now(),
            'iat': iat_now()
        }
        access_token = {
            'iss': op_conf["sub"],
            'sub': '2ed008b45e66ce53e48273dca5a4463bc8ebd036ebaa824f4582627683c2451b',
            'aud': [rp_conf["metadata"]["openid_relying_party"]["client_id"], ],
            'client_id': rp_conf["metadata"]["openid_relying_party"]["client_id"],
            'scope': 'openid',
            'jti': '402e61bd-950c-4934-83d4-c09a05468828',
            'exp': exp_from_now(),
            'iat': iat_now()
        }
        self.jwt_at = create_jws(access_token, op_conf_priv_jwk, typ="at+jwt")
        id_token['at_hash'] = left_hash(self.jwt_at, "HS256")
        self.jwt_id = create_jws(id_token, op_conf_priv_jwk)

        session = OidcSession.objects.create(
            user=User.objects.create(username="username"),
            user_uid="",
            nonce="",
            authz_request={"scope": "offline_access", "prompt": "consent", "nonce": "123",
                           "acr_values": ["https://www.spid.gov.it/SpidL2", "https://www.spid.gov.it/SpidL1"]},
            client_id=RP_SUB,
            auth_code="code",
        )
        IssuedToken.objects.create(
            refresh_token=self.rt_jws,
            id_token=self.jwt_id,
            access_token=self.jwt_at,
            session=session,
            expires=timezone.localtime()
        )
        self.assertEqual(refresh_token["iss"], self.op_local_conf["sub"])

    @override_settings(OIDCFED_PROVIDER_PROFILE="spid")
    def test_grant_refresh_token_spid(self):
        client = Client()
        url = reverse("oidc_provider_token_endpoint")
        request = dict(
            client_id=RP_CLIENT_ID,
            client_assertion=self.ca_jws,
            client_assertion_type="urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            refresh_token=self.rt_jws,
            grant_type="refresh_token"
        )
        res = client.post(url, request)
        self.assertTrue(res.status_code == 200)
        refresh_token = verify_jws(res.json().get("refresh_token"), op_conf_priv_jwk)
        self.assertEqual(refresh_token["aud"], RP_CLIENT_ID)
        self.assertEqual(refresh_token["iss"], self.op_local_conf["sub"])

    @override_settings(OIDCFED_PROVIDER_PROFILE="cie")
    def test_grant_refresh_token_cie(self):
        client = Client()
        url = reverse("oidc_provider_token_endpoint")
        request = dict(
            client_id=RP_CLIENT_ID,
            client_assertion=self.ca_jws,
            client_assertion_type="urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            refresh_token=self.rt_jws,
            grant_type="refresh_token"
        )
        res = client.post(url, request)
        self.assertTrue(res.status_code == 200)
        refresh_token = verify_jws(res.json().get("refresh_token"), op_conf_priv_jwk)
        self.assertEqual(refresh_token["aud"], RP_CLIENT_ID)

    @override_settings(OIDCFED_PROVIDER_MAX_REFRESH=1, OIDCFED_PROVIDER_PROFILE="spid")
    def test_grant_refresh_token_two_times_spid(self):
            client = Client()
            url = reverse("oidc_provider_token_endpoint")
            request = dict(
                client_id=RP_CLIENT_ID,
                client_assertion=self.ca_jws,
                client_assertion_type="urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
                refresh_token=self.rt_jws,
                grant_type="refresh_token"
            )
            res = client.post(url, request)
            self.assertTrue(res.status_code == 200)
            request = dict(
                client_id=RP_CLIENT_ID,
                client_assertion=self.ca_jws,
                client_assertion_type="urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
                refresh_token=res.json()["refresh_token"],
                grant_type="refresh_token"
            )
            res = client.post(url, request)
            self.assertTrue(res.status_code == 400)

    @override_settings(OIDCFED_PROVIDER_MAX_CONSENT_TIMEFRAME=1, OIDCFED_PROVIDER_PROFILE="cie")
    def test_grant_refresh_token_two_times_cie(self):
        client = Client()
        url = reverse("oidc_provider_token_endpoint")
        request = dict(
            client_id=RP_CLIENT_ID,
            client_assertion=self.ca_jws,
            client_assertion_type="urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            refresh_token=self.rt_jws,
            grant_type="refresh_token"
        )
        res = client.post(url, request)
        self.assertTrue(res.status_code == 200)
        request = dict(
            client_id=RP_CLIENT_ID,
            client_assertion=self.ca_jws,
            client_assertion_type="urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            refresh_token=res.json()["refresh_token"],
            grant_type="refresh_token"
        )
        time.sleep(2)
        res = client.post(url, request)
        self.assertTrue(res.status_code == 400)
