
from unittest.mock import patch

from django.http import HttpRequest
from django.test import TestCase, override_settings
from django.conf import settings
from spid_cie_oidc.authority.tests.mocked_responses import EntityResponseNoIntermediate
from spid_cie_oidc.authority.tests.settings import *
from spid_cie_oidc.entity.jwtse import create_jws
from spid_cie_oidc.entity.jwks import create_jwk
from spid_cie_oidc.entity.models import (FederationEntityConfiguration, FetchedEntityStatement,
                                         TrustChain)
from spid_cie_oidc.entity.statements import EntityConfiguration, get_entity_configurations
from spid_cie_oidc.entity.tests.settings import *
from spid_cie_oidc.entity.trust_chain_operations import  get_or_create_trust_chain
from spid_cie_oidc.entity.utils import datetime_from_timestamp, exp_from_now, iat_now
from spid_cie_oidc.provider.views import authn_request
from spid_cie_oidc.provider.settings import *

JWK={'kty': 'RSA', 'kid': 'Zo3_0sgHWTMZ42ExVZNbV7wN_ZO_rX9S66GyQHkpsgg', 'e': 'AQAB', 'n': '3i5vV-_4nF_ES1BU86Zf2Bj6SiyGdGM3Izc2GrvtknQQCzpT3QlGv2d_wMrzVTS7PmZlvjyi2Qceq8EmEwbsIa5R8G57fxSpE0HL33giJfhpe8ublY4hGb6tEqSbHiFcgiF4T-Ft_98pz4nZtKTcesMZ8CcDUd9ibaLXGM4vaiUhSt76X1qOzqJHqAKMG-9VGm5DD2GSe7cu1yvaMCMPU6DGOqHYoBSkSbsnLelsRg6sINh6mZfb39odTJlOMFGhlg665702kc_iqqxd8jpyOh94vBagmJB4EQqI1qEte8sTMeBkVRpSLDoV5uNTlp2ZdINu1SakmaHB3WeStwC1lw', 'd': 'QvPRP7mjvFOrjlp9zxJyzWbxfYqfVdFUGzuXBUVeWQS6lPeVsAUMmb8xo0JFQ4bpaetne4VAOZBIsM86jv9GBvxF2uMgOfJa5N-t9QB5oeGSv-hiURYMaXqpIvYRfGnnO5ukasXu5O0150GOJj6L5j6GwXSwLmrXeVxZ3zK63QwVl71xU1LR-lO0wLbqQROIT37Jw72B__wBk3QC0HjbrPv1fUVxKB3RCDR43X7PQkMPOfRHxicyp2MA4mLhLvuoRTTI4dfnd8Ou-xX5ctVzYmL0EMxPCleDFDIn9gTxpgCH95sVi-Zg6Zw5k1J_cchoD4AgGSSt2dr9mbiTRjLlcQ', 'p': '8BHX7hErQjESybgfzcX0hZmM-e1EWaM76uNJop9BiqRlBz9f-XxuC40A032AaZFDXqxVi3W0Hn1vJA6lSj9mGY5HEY-YVWAdOLLjM12oQ_cnH6czElExAoppUeMWsDEewDbZTn6rX5silcZ8Pu7Tsj-KSjPVzl9dr1w76EzsYj8', 'q': '7Oy3PGm3MjVlgTlgHnRKC-IcoB50hCBiqwACVcnlIgpg9Kt_srV7NWdmo5DJFIdrrvkjmN4wi9IOknSymStU-sB8BepnnterjPyBOr9PbttUP13qcOjuvjzD7Tr0IGou3yhA-YOuO9hOluhqd4tJIkdxT_X9qxgFQx5NSnsBpqk'}
HEADER = {'client_id':'http://127.0.0.1:8000/oidc/rp/', 'type':'self.ta_conf.sub,code', 'scope':'openid', 'code_challenge':'qWJlMe0xdbXrKxTm72EpH659bUxAxw80','code_challenge_method':'S256'}

METADATA = {
    'application_type': 'web', 
    'client_registration_types': ['automatic'], 
    'client_name': 'Name of this service called https://rp.example.it/spid', 
    'contacts': ['ops@rp.example.it'], 
    'grant_types': ['refresh_token', 'authorization_code'], 
    'redirect_uris': ['https://rp.example.it/spid/callback'], 
    'response_types': ['code'], 
    'subject_type': 'pairwise', 
    'jwks': [{'kty': 'RSA', 'e': 'AQAB', 'n': 'zme8SSfV64_vziLznM93khQQZgTY22HNWRY6E3ehQotDUxm5QWS5oVUOIYfwEOr3cgIlHvJZZipjxsiyJHR62eI1HjwXfaxa-AtleCDMnJOQ97YivYBvkt1LSS3oXHYqHCSNxcvYLmeTHZa4o_M6rj0J6n6ihh0JbA6R3XnKqZ0lYt1CHv6uWbojz5s4qsAF0Z5XmsjyUOYlsG4uOuy8ntur9cRwZ0BXERaVt9l0fgNoBQjzJKjgKbZVmM4Pv55FCT7iwO_BATXENn8Zju4zVyD7TvawT9HFsjd-8M8QK9KAJ59_P4Olxp_S_xwnGHNA4rMh4aQJQaEfB6yYAEN7rw', 'kid': 'Zo3_0sgHWTMZ42ExVZNbV7wN_ZO_rX9S66GyQHkpsgg'}]
    }

PAYLOAD = {'client_id': 'http://127.0.0.1:8000/oidc/rp/', 'sub': 'http://rp-test/oidc/rp','iss': 'http://rp-test/oidc/rp','response_type': 'code', 'scope': 'openid', 'code_challenge': 'qWJlMe0xdbXrKxTm72EpH659bUxAxw80', 'code_challenge_method': 'S256', 'nonce': 'MBzGqyf9QytD28eupyWhSqMj78WNqpc2', 'prompt': 'consent login', 'redirect_uri': 'https://rp.cie.it/callback1/', 'acr_values': 'CIE_L1 CIE_L2', 'claims': {'id_token': {'family_name': {'essential': True}, 'email': {'essential': True}}, 'userinfo': {'name': None, 'family_name': None}}, 'state': 'fyZiOL9Lf2CeKuNT2JzxiLRDink0uPcd'}

class AuthnRequestTest(TestCase):

    @override_settings(HTTP_CLIENT_SYNC=True)
    @patch("requests.get", return_value=EntityResponseNoIntermediate())
    def setUp(self, mocked):
        self.req = HttpRequest()
        jwk = create_jwk()
        jws=create_jws(PAYLOAD,jwk)
        self.req.GET = {'header':HEADER, 'request':jws}
        self.ta_conf = FederationEntityConfiguration.objects.create(**ta_conf_data)
        jwt = get_entity_configurations(self.ta_conf.sub)
        trust_anchor_ec = EntityConfiguration(jwt[0])
        trust_anchor_ec.is_valid = True
        breakpoint()

        fes = FetchedEntityStatement.objects.create(
            sub = ["http://127.0.0.1:8000/"],
            iss = "http://127.0.0.1:8000/",
            **TA_STATMENT
            )
        breakpoint()
        TrustChain.objects.create(
            sub = 'http://127.0.0.1:8000/oidc/rp/',
            type = "openid_relying_party",
            metadata = METADATA,
            status = 'valid',
            trust_anchor = fes,
            is_active = True
            )
        breakpoint()
        

    def test_auth_request(self):
        authn_request(self.req)


