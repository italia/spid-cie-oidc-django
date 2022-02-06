import logging

from cryptojwt.exception import BadSyntax
from requests.auth import HTTPBasicAuth
from . utils import (decode_token,
                     validate_jwt)


logger = logging.getLogger(__name__)


class OAuth2BaseView(object):
    def validate_jwt(self, authz, jwt, keyjar):
        _msg = (f'Something went wrong with {authz} JWT validation: '
                'Token validation fails [jwt]')
        if validate_jwt(jwt, key_jar=keyjar):
            return True
        else:
            logger.error(_msg)
            return False

    def decode_jwt(self, name, authz, jwt, keyjar):
        try:
            decoded_jwt = decode_token(jwt, keyjar=keyjar)
            logger.debug(f"{name}: {decoded_jwt}")
            return decoded_jwt
        except BadSyntax:
            logger.warning(
                f"{name} from {authz.issuer} is not in JWT format: {jwt}"
            )
        except Exception as e: # pragma: no cover
            logger.error(f"Something went wrong decoding {name}: {e}")
