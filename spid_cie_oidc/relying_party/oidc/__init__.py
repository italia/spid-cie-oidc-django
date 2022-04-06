import logging
import requests
from spid_cie_oidc.entity.exceptions import UnknownKid
from spid_cie_oidc.entity.jwtse import unpad_jwt_head, decrypt_jwe, verify_jws

logger = logging.getLogger(__name__)


class OidcUserInfo(object):
    """
    https://openid.net/specs/openid-connect-core-1_0.html#UserInfo
    """

    def get_jwk(self, kid, jwks):
        for jwk in jwks:
            if jwk.get("kid", None) and jwk["kid"] == kid:
                return jwk
        raise UnknownKid() # pragma: no cover

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

        if authz_userinfo.status_code != 200: # pragma: no cover
            logger.error(
                f"Something went wrong with {state}: {authz_userinfo.status_code}"
            )
            return False
        else:
            try:
                jwe = authz_userinfo.content.decode()
                header = unpad_jwt_head(jwe)
                # header["kid"] kid di rp
                rp_jwk = self.get_jwk(header["kid"], self.rp_conf.jwks)
                jws = decrypt_jwe(jwe, rp_jwk)

                header = unpad_jwt_head(jws)
                idp_jwks = provider_conf["jwks"]["keys"]
                idp_jwk = self.get_jwk(header["kid"], idp_jwks)

                decoded_jwt = verify_jws(jws, idp_jwk)
                logger.debug(f"Userinfo endpoint result: {decoded_jwt}")
                return decoded_jwt

            except KeyError as e: # pragma: no cover
                logger.error(f"Userinfo response error {state}: {e}")
                return False
            except UnknownKid as e:
                logger.error(f"Userinfo Unknow KID for session {state}: {e}")
                return False
            except Exception as e:  # pragma: no cover
                logger.error(f"Userinfo response unknown error {state}: {e}")
                return False
