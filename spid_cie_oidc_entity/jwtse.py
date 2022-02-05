import base64
import binascii
import json
import logging

from cryptojwt.exception import UnsupportedAlgorithm, VerificationError
from cryptojwt.jwe.jwe import factory
from cryptojwt.jwe.jwe_rsa import JWE_RSA
from cryptojwt.jwk.jwk import key_from_jwk_dict
from cryptojwt.jws.jws import JWS
from django.conf import settings

from . import settings as local_settings

JWS_ALG = getattr(
    settings, "DEFAULT_JWS_ALG", local_settings.DEFAULT_JWS_ALG
)
JWE_ALG = getattr(
    settings, "DEFAULT_JWE_ALG", local_settings.DEFAULT_JWE_ALG
)
JWE_ENC = getattr(
    settings, "DEFAULT_JWE_ENC", local_settings.DEFAULT_JWE_ENC
)
DISABLED_JWT_ALGS = getattr(
    settings, "DISABLED_JWT_ALGS", local_settings.DISABLED_JWT_ALGS
)
logger = logging.getLogger(__name__)


def unpad_jwt_head(jwt):
    b = jwt.split(".")[0]
    padded = f"{b}{'=' * divmod(len(b),4)[1]}"
    jwe_header = json.loads(base64.b64decode(padded))
    return jwe_header


def encrypt_dict(plain_dict, jwk_dict) -> str:
    logger.debug(f"Encrypting dict as JWE: " f"{plain_dict}")
    _key = key_from_jwk_dict(jwk_dict)
    _rsa = JWE_RSA(
        json.dumps(plain_dict).encode(),
        alg=JWE_ALG,
        enc=JWE_ENC,
        kid=_key.kid
    )
    jwe = _rsa.encrypt(_key.public_key())
    logger.debug(f"Encrypted dict as JWE: {jwe}")
    return jwe


def decrypt_jwe(jwe, jwk_dict) -> dict:
    # get header
    try:
        jwe_header = unpad_jwt_head(jwe)
    except (binascii.Error, Exception) as e:
        logger.error(f"Failed to extract JWT header: {e}")
        raise VerificationError("The JWT is not valid")

    _alg = jwe_header.get("alg", JWE_ALG)
    _enc = jwe_header.get("enc", JWE_ENC)
    jwe_header.get("kid")

    if _alg in DISABLED_JWT_ALGS:
        raise UnsupportedAlgorithm(
            f"{_alg} has beed disabled for security reason"
        )

    _decryptor = factory(jwe, alg=_alg, enc=_enc)

    # _dkey = RSAKey(priv_key=PRIV_KEY)
    _dkey = key_from_jwk_dict(jwk_dict)
    msg = _decryptor.decrypt(jwe, [_dkey])

    msg_dict = json.loads(msg)
    logger.debug(f"Decrypted JWT as: {json.dumps(msg_dict, indent=2)}")
    return msg_dict


def create_jws(
            payload:dict, jwk_dict:dict, alg:str = "RS256", headers:dict = {}
) -> str:

    headers['kid'] = jwk_dict['kid']
    headers['alg'] = alg

    _key = key_from_jwk_dict(jwk_dict)
    _signer = JWS(payload, alg=alg)

    base64.urlsafe_b64encode(json.dumps(headers).encode())
    base64.urlsafe_b64encode(json.dumps(payload).encode())
    signature = _signer.sign_compact([_key])
    return signature


def verify_jws(jws:str, pub_jwk:dict):
    _key = key_from_jwk_dict(pub_jwk)

    _head = unpad_jwt_head(jws)
    if _head.get('kid') != pub_jwk['kid']:
        raise Exception(f"kid error: {_head.get('kid')} != {pub_jwk['kid']}")

    _alg = _head['alg']
    if _alg in DISABLED_JWT_ALGS or not _alg:
        raise UnsupportedAlgorithm(
            f"{_alg} has beed disabled for security reason"
        )

    verifier = JWS(alg=_head['alg'])
    msg = verifier.verify_compact(jws, [_key])
    return msg
