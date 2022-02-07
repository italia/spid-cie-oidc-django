import json
import logging
import requests

from cryptojwt.jwk.jwk import key_from_jwk_dict
from django.utils.translation import gettext as _


logger = logging.getLogger(__name__)


class OidcUserInfo(object):
    """
        https://openid.net/specs/openid-connect-core-1_0.html#UserInfo
    """
    def get_userinfo(self,
                     state:str,
                     access_token:str,
                     provider_conf:dict,
                     verify:bool):
        """
            User Info endpoint request with bearer access token
        """
        # userinfo
        headers = {'Authorization': f'Bearer {access_token}'}
        authz_userinfo = requests.get(provider_conf['userinfo_endpoint'],
                                      headers=headers, verify=verify)
        if authz_userinfo.status_code != 200: # pragma: no cover
            logger.error(
                f'Something went wrong with {state}: {authz_userinfo.content}'
            )
            return False
        else:
            try:
                authz_userinfo = json.loads(authz_userinfo.content.decode())
                logger.debug(f"Userinfo endpoint result: {authz_userinfo}")
                return authz_userinfo
            except Exception as e: # pragma: no cover
                logger.error(f'Something went wrong with {state}: {e}')
                return False
