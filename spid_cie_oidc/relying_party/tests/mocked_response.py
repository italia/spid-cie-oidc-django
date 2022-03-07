import json
import logging

from django.http import HttpResponse
from spid_cie_oidc.entity.models import FederationEntityConfiguration

from spid_cie_oidc.provider.tests.settings import op_conf
from spid_cie_oidc.authority.tests.settings import RP_METADATA_JWK1_pub, rp_conf
from spid_cie_oidc.entity.jwtse import create_jws, encrypt_dict
from spid_cie_oidc.entity.utils import iat_now, exp_from_now
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
        jwt_at = create_jws(access_token, op_conf['jwks'][0], typ="at+jwt")
        jwt_id = create_jws(id_token, op_conf['jwks'][0])

        res = {
                "access_token": jwt_at,
                "id_token": jwt_id,
                "token_type": "bearer",
                "expires_in": 3600,
                "scope": "openid",
            }
        return json.dumps(res).encode()

class MockedUserinfoEndPointResponse:
    def __init__(self):
        self.status_code = 200

    @property
    def content(self):

        rp_conf_saved = FederationEntityConfiguration.objects.all().first()  
        
        userinfo = {
                    "iss": op_conf["sub"],
                    "aud": [rp_conf["metadata"]["openid_relying_party"]["client_id"],], 
                    "iat": iat_now(),
                    "nbf": iat_now(),
                    "exp": exp_from_now(),
                    "sub": '2ed008b45e66ce53e48273dca5a4463bc8ebd036ebaa824f4582627683c2451b',
                    "name": "Mario",
                    "family_name": "Rossi",
                    "tax_number": "MROXXXXXXXXXXXXX"
        }
        jwt = create_jws(userinfo, op_conf['jwks'][0], typ="at+jwt")
        #jwe = encrypt_dict(jwt, rp_conf['metadata']['openid_relying_party']['jwks']['keys'][0])
        breakpoint()
        jwe = encrypt_dict(jwt, rp_conf_saved.metadata["openid_relying_party"]["jwks"]["keys"][0])
        return HttpResponse(jwe, content_type="application/jose").content