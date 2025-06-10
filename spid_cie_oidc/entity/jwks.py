from cryptojwt.jwk.jwk import key_from_jwk_dict
from cryptojwt.jwk.rsa import new_rsa_key
from cryptojwt.jwk.ec import new_ec_key
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptojwt.jwk.rsa import RSAKey
from cryptojwt.jwk.ec import ECKey
from cryptography.hazmat.primitives.asymmetric import rsa, ec

import cryptography
from django.conf import settings

from . import settings as local_settings


DEFAULT_HASH_FUNC = getattr(
    settings, "DEFAULT_HASH_FUNC", local_settings.DEFAULT_HASH_FUNC
)

def create_jwk(key = None, hash_func=None, typ :str = getattr(settings, "PRIVATE_KEY_TYPE", None)):
    if key:
        key = key
    elif typ and typ.lower() == 'ec':
        key = new_ec_key(crv="P-256")
    else:
        key = new_rsa_key()

    thumbprint = key.thumbprint(hash_function=hash_func or DEFAULT_HASH_FUNC)
    jwk = key.to_dict()
    jwk["kid"] = thumbprint.decode()
    return jwk


def public_jwk_from_private_jwk(jwk_dict: dict):
    # exports public
    _k = key_from_jwk_dict(jwk_dict)
    jwk = _k.serialize()
    jwk["kid"] = jwk_dict['kid']
    return jwk


def private_pem_from_jwk(jwk_dict: dict):
    # exports private

    _k = key_from_jwk_dict(jwk_dict)
    pk = _k.private_key()
    pem = pk.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return pem.decode()


def public_pem_from_jwk(jwk_dict: dict):
    # exports private

    _k = key_from_jwk_dict(jwk_dict)
    pk = _k.public_key()
    cert = pk.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return cert.decode()

def serialize_key(key, kind="public", hash_func="SHA-256"):
    """
    key can be:
        - cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey
        - cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey
        - cryptography.hazmat.primitives.asymmetric.ec.EllipticCurvePublicKey
        - cryptography.hazmat.primitives.asymmetric.ec.EllipticCurvePrivateKey
        - str or bytes (PEM format)
    """
    data = {}
    
    # Handle RSA keys
    if isinstance(key, rsa.RSAPublicKey):
        data = {"pub_key": key}
    elif isinstance(key, rsa.RSAPrivateKey):
        data = {"priv_key": key}
    # Handle EC keys
    elif isinstance(key, ec.EllipticCurvePublicKey):
        data = {"pub_key": key}
    elif isinstance(key, ec.EllipticCurvePrivateKey):
        data = {"priv_key": key}
    # Handle PEM strings/bytes
    elif isinstance(key, (str, bytes)):
        if kind == "private":
            if isinstance(key, rsa.RSAPrivateKey) or (isinstance(key, str) and "RSA" in key):
                data = {"priv_key": private_jwk_from_pem(key)}
            else:
                data = {"priv_key": private_jwk_from_pem(key)}
        else:
            if isinstance(key, rsa.RSAPublicKey) or (isinstance(key, str) and "RSA" in key):
                data = {"pub_key": public_jwk_from_pem(key)}
            else:
                data = {"pub_key": public_jwk_from_pem(key)}

    # Create appropriate JWK object based on key type
    if isinstance(key, (rsa.RSAPublicKey, rsa.RSAPrivateKey)) or (isinstance(key, str) and "RSA" in key):
        jwk_obj = RSAKey(**data)
    else:
        jwk_obj = ECKey(**data)

    thumbprint = jwk_obj.thumbprint(hash_function=hash_func)
    jwk = jwk_obj.to_dict()
    jwk["kid"] = thumbprint.hex()  # Use hex() instead of decode()
    return jwk


def private_jwk_from_pem(content:str, password:str = None):
    content = content.encode() if isinstance(content, str) else content
    key = serialization.load_pem_private_key(content, password=password)
    return serialize_key(key, kind='private')


def public_jwk_from_pem(content:str, password:str = None):
    content = content.encode() if isinstance(content, str) else content
    key = serialization.load_pem_public_key(content)
    return serialize_key(key, kind='public')
