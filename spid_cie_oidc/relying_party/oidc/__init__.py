import json
import logging
import requests
from spid_cie_oidc.entity.jwtse import (
    unpad_jwt_head, 
    decrypt_jwe, 
    unpad_jwt_payload, 
    verify_jws
)

logger = logging.getLogger(__name__)


class OidcUserInfo(object):
    """
    https://openid.net/specs/openid-connect-core-1_0.html#UserInfo
    """
    def get_jwk(kid, jwks):
        jwk = {}
        for jwk in jwks:
            if jwk["kid"] == kid:
                return jwk
        if not jwk:
            raise Exception()

    def get_userinfo(
        self, state: str, access_token: str, provider_conf: dict, verify: bool
    ):
        """
        User Info endpoint request with bearer access token
        """
        # userinfo
        headers = {"Authorization": f"Bearer {access_token}"}
        authz_userinfo = requests.get(
            provider_conf["userinfo_endpoint"], headers=headers, verify=verify
        )
        if authz_userinfo.status_code != 200:  # pragma: no cover
            logger.error(f"Something went wrong with {state}: {authz_userinfo.content}")
            return False
        else:
            try:
                header = unpad_jwt_head(authz_userinfo)
                jwe = unpad_jwt_payload(authz_userinfo)
                kid = header["kid"]
                jwks = provider_conf["openid_provider"]["metadata"]["jwks"]["keys"]
                jwk = self.get_jwk(kid, jwks)
                jws = decrypt_jwe(jwe, jwk)
                verify_jws(jws, jwk)
                # TODO: Francesca, qui devi fare unpad dell'header
                # prendere alg e kid
                # decriptare col jwk relativo a questo kid
                # verificare il jwt decriptato

                authz_userinfo = json.loads(authz_userinfo.content.decode())
                logger.debug(f"Userinfo endpoint result: {authz_userinfo}")
                return authz_userinfo
            except Exception as e:  # pragma: no cover
                logger.error(f"Something went wrong with {state}: {e}")
                return False
