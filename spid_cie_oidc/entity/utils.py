from django.utils import timezone
from django.utils.timezone import make_aware

from secrets import token_hex
from spid_cie_oidc.entity.jwtse import unpad_jwt_head
from spid_cie_oidc.entity.settings import HTTPC_PARAMS
from spid_cie_oidc.entity.statements import get_http_url


import datetime
import logging

logger = logging.getLogger(__name__)


def iat_now() -> int:
    return int(datetime.datetime.now().timestamp())


def exp_from_now(minutes: int = 33) -> int:
    _now = timezone.localtime()
    return int((_now + datetime.timedelta(minutes=minutes)).timestamp())


def datetime_from_timestamp(value) -> datetime.datetime:
    return make_aware(datetime.datetime.fromtimestamp(value))


def get_jwks(metadata: dict, federation_jwks:list = []) -> dict:
    """
    get jwks or jwks_uri or signed_jwks_uri
    """
    jwks_list = []
    if metadata.get('jwks'):
        jwks_list = metadata["jwks"]["keys"]
    elif metadata.get('jwks_uri'):
        try:
            jwks_uri = metadata["jwks_uri"]
            jwks_list = get_http_url(
                [jwks_uri], httpc_params=HTTPC_PARAMS
            ).json()
        except Exception as e:
            logger.error(f"Failed to download jwks from {jwks_uri}: {e}")
    elif metadata.get('signed_jwks_uri'):
        try:
            signed_jwks_uri = metadata["signed_jwks_uri"]
            jwks_list = get_http_url(
                [signed_jwks_uri], httpc_params=HTTPC_PARAMS
            )[0]
        except Exception as e:
            logger.error(f"Failed to download jwks from {signed_jwks_uri}: {e}")
    return jwks_list


def get_jwk_from_jwt(jwt: str, provider_jwks: dict) -> dict:
    """
        docs here
    """
    head = unpad_jwt_head(jwt)
    kid = head["kid"]
    for jwk in provider_jwks:
        if jwk["kid"] == kid:
            return jwk
    return {}


def random_token(n=254):
    return token_hex(n)
