import base64
import binascii
import json
import logging

from cryptojwt.exception import UnsupportedAlgorithm, VerificationError
from cryptojwt.jwe.jwe import factory
from cryptojwt.jwe.jwe_rsa import JWE_RSA
from cryptojwt.jwk.jwk import key_from_jwk_dict
from cryptojwt.jws.jws import JWS
from typing import Union

from .settings import (
    DEFAULT_JWE_ALG,
    DEFAULT_JWE_ENC,
    ENCRYPTION_ALG_VALUES_SUPPORTED,
    SIGNING_ALG_VALUES_SUPPORTED,
)


logger = logging.getLogger(__name__)


def unpad_jwt_element(jwt: str, position: int) -> dict:
    b = jwt.split(".")[position]
    padded = f"{b}{'=' * divmod(len(b),4)[1]}"
    data = json.loads(base64.urlsafe_b64decode(padded))
    return data


def unpad_jwt_head(jwt: str) -> dict:
    return unpad_jwt_element(jwt, position=0)


def unpad_jwt_payload(jwt: str) -> dict:
    return unpad_jwt_element(jwt, position=1)


def create_jwe(plain_dict: Union[dict, None], jwk_dict: dict, **kwargs) -> str:
    logger.debug(f"Encrypting dict as JWE: " f"{plain_dict}")
    _key = key_from_jwk_dict(jwk_dict)
    _rsa = JWE_RSA(
        json.dumps(plain_dict).encode(),
        alg=DEFAULT_JWE_ALG,
        enc=DEFAULT_JWE_ENC,
        kid=_key.kid,
        **kwargs
    )
    jwe = _rsa.encrypt(_key.public_key())
    logger.debug(f"Encrypted dict as JWE: {jwe}")
    return jwe


def decrypt_jwe(jwe: str, jwk_dict: dict) -> dict:
    # get header
    try:
        jwe_header = unpad_jwt_head(jwe)
    except (binascii.Error, Exception) as e: # pragma: no cover
        logger.error(f"Failed to extract JWT header: {e}")
        raise VerificationError("The JWT is not valid")

    _alg = jwe_header.get("alg", DEFAULT_JWE_ALG)
    _enc = jwe_header.get("enc", DEFAULT_JWE_ENC)
    jwe_header.get("kid")

    if _alg not in ENCRYPTION_ALG_VALUES_SUPPORTED: # pragma: no cover
        raise UnsupportedAlgorithm(f"{_alg} has beed disabled for security reason")

    _decryptor = factory(jwe, alg=_alg, enc=_enc)

    # _dkey = RSAKey(priv_key=PRIV_KEY)
    _dkey = key_from_jwk_dict(jwk_dict)
    msg = _decryptor.decrypt(jwe, [_dkey])

    msg_dict = json.loads(msg)
    logger.debug(f"Decrypted JWT as: {json.dumps(msg_dict, indent=2)}")
    return msg_dict


def create_jws(payload: dict, jwk_dict: dict, alg: str = "RS256", **kwargs) -> str:

    _key = key_from_jwk_dict(jwk_dict)
    _signer = JWS(payload, alg=alg, **kwargs)

    signature = _signer.sign_compact([_key])
    return signature


def verify_jws(jws: str, pub_jwk: dict, **kwargs) -> str:
    _key = key_from_jwk_dict(pub_jwk)

    _head = unpad_jwt_head(jws)
    if _head.get("kid") != pub_jwk["kid"]: # pragma: no cover
        raise Exception(
            f"kid error: {_head.get('kid')} != {pub_jwk['kid']}"
        )

    _alg = _head["alg"]
    if _alg not in SIGNING_ALG_VALUES_SUPPORTED or not _alg: # pragma: no cover
        raise UnsupportedAlgorithm(f"{_alg} has beed disabled for security reason")

    verifier = JWS(alg=_head["alg"], **kwargs)
    msg = verifier.verify_compact(jws, [_key])
    return msg
