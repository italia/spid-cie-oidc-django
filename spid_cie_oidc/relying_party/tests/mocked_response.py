import json
import logging


from spid_cie_oidc.provider.tests.settings import op_conf, op_conf_priv_jwk
from spid_cie_oidc.authority.tests.settings import rp_conf, INTERMEDIARY_JWK1
from spid_cie_oidc.entity.jwtse import create_jws, create_jwe
from spid_cie_oidc.entity.utils import iat_now, exp_from_now
from spid_cie_oidc.entity.utils import get_jwks
logger = logging.getLogger(__name__)


class MockedTokenEndPointResponse:
    def __init__(self):
        self.status_code = 200

    @property
    def content(self):
        id_token = {
            'sub': '2ed008b45e66ce53e48273dca5a4463bc8ebd036ebaa824f4582627683c2451b', 
            'nonce': 'ljbvL3rpscgS4ZGda7cgibXHr7vrNREW', 
            'at_hash': 'u2RjeYbZSJZO55XwY2LJew', 
            'c_hash': 'tij0h-zL_bSrsVXy-d3qHw', 
            'aud': [rp_conf["metadata"]["openid_relying_party"]["client_id"],], 
            'iss': op_conf["sub"], 
            'jti': '402e61bd-950c-4934-83d4-c09a05468828', 
            'exp': exp_from_now(), 
            'iat': iat_now()
        }
        access_token = {
            'iss': op_conf["sub"], 
            'sub': '2ed008b45e66ce53e48273dca5a4463bc8ebd036ebaa824f4582627683c2451b', 
            'aud': [rp_conf["metadata"]["openid_relying_party"]["client_id"],], 
            'client_id': rp_conf["metadata"]["openid_relying_party"]["client_id"],
            'scope': 'openid', 
            'jti': '402e61bd-950c-4934-83d4-c09a05468828', 
            'exp': exp_from_now(), 
            'iat': iat_now()
        }
        jwt_at = create_jws(access_token, op_conf_priv_jwk, typ="at+jwt")
        jwt_id = create_jws(id_token, op_conf_priv_jwk)

        self.access_token = jwt_at
        self.id_token = jwt_id

        res = {
                "access_token": jwt_at,
                "id_token": jwt_id,
                "token_type": "Bearer",
                "expires_in": 3600,
                "scope": "openid",
            }
        return json.dumps(res).encode()

class MockedTokenEndPointNoCorrectResponse:
    def __init__(self):
        self.status_code = 200

    @property
    def content(self):
        id_token = {
            'sub': '2ed008b45e66ce53e48273dca5a4463bc8ebd036ebaa824f4582627683c2451b', 
            'nonce': 'ljbvL3rpscgS4ZGda7cgibXHr7vrNREW', 
            'at_hash': 'u2RjeYbZSJZO55XwY2LJew', 
            'c_hash': 'tij0h-zL_bSrsVXy-d3qHw', 
            'aud': [rp_conf["metadata"]["openid_relying_party"]["client_id"],], 
            'iss': op_conf["sub"], 
            'jti': '402e61bd-950c-4934-83d4-c09a05468828', 
            'exp': exp_from_now(), 
            'iat': iat_now()
        }
        access_token = {
            'iss': op_conf["sub"], 
            'sub': '2ed008b45e66ce53e48273dca5a4463bc8ebd036ebaa824f4582627683c2451b', 
            'aud': [rp_conf["metadata"]["openid_relying_party"]["client_id"],], 
            'client_id': rp_conf["metadata"]["openid_relying_party"]["client_id"],
            'scope': 'openid', 
            'jti': '402e61bd-950c-4934-83d4-c09a05468828', 
            'exp': exp_from_now(), 
            'iat': iat_now()
        }
        jwt_at = create_jws(access_token, op_conf_priv_jwk, typ="at+jwt")
        jwt_id = create_jws(id_token, op_conf_priv_jwk)

        self.access_token = jwt_at
        self.id_token = jwt_id

        res = {
                "access_token": jwt_at,
                "token_type": "Bearer",
                "expires_in": 3600,
                "scope": "openid",
            }
        return json.dumps(res).encode()



class MockedTokenEndPointNoCorrectIdTokenResponse:
    def __init__(self):
        self.status_code = 200

    @property
    def content(self):
        id_token = {
            'sub': '2ed008b45e66ce53e48273dca5a4463bc8ebd036ebaa824f4582627683c2451b', 
            'nonce': 'ljbvL3rpscgS4ZGda7cgibXHr7vrNREW', 
            'at_hash': 'u2RjeYbZSJZO55XwY2LJew', 
            'c_hash': 'tij0h-zL_bSrsVXy-d3qHw', 
            'aud': [rp_conf["metadata"]["openid_relying_party"]["client_id"],], 
            'iss': op_conf["sub"], 
            'jti': '402e61bd-950c-4934-83d4-c09a05468828', 
            'exp': exp_from_now(), 
            'iat': iat_now()
        }
        access_token = {
            'iss': op_conf["sub"], 
            'sub': '2ed008b45e66ce53e48273dca5a4463bc8ebd036ebaa824f4582627683c2451b', 
            'aud': [rp_conf["metadata"]["openid_relying_party"]["client_id"],], 
            'client_id': rp_conf["metadata"]["openid_relying_party"]["client_id"],
            'scope': 'openid', 
            'jti': '402e61bd-950c-4934-83d4-c09a05468828', 
            'exp': exp_from_now(), 
            'iat': iat_now()
        }
        jwt_at = create_jws(access_token, op_conf_priv_jwk, typ="at+jwt")
        jwt_id = create_jws(id_token, INTERMEDIARY_JWK1)

        self.access_token = jwt_at
        self.id_token = jwt_id

        res = {
                "access_token": jwt_at,
                "token_type": "Bearer",
                "id_token": jwt_id,
                "expires_in": 3600,
                "scope": "openid",
            }
        return json.dumps(res).encode()

class MockedUserInfoResponse:
    def __init__(self):
        self.status_code = 200

    @property
    def content(self):
        jwt = {
            "sub": 'asdasdasdasasdasdas',
            "https://attributes.spid.gov.it/fiscalNumber": "sdfsfs908df09s8df90s8fd0"
        }
        jws = create_jws(jwt, op_conf_priv_jwk)
        jwe = create_jwe(
            jws, 
            get_jwks(rp_conf["metadata"]["openid_relying_party"])[0]
        )
        return jwe.encode()

class MockedLogout:

    @property
    def content(self):
        pass
    
