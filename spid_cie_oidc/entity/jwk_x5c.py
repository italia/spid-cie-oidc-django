import base64
from urllib.parse import urlparse
from typing import Union

from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import ec, ed25519, ed448, rsa
from cryptojwt.jwk.jwk import key_from_jwk_dict

from spid_cie_oidc.entity.x509 import X509Issuer


def _public_key_from_jwk_dict(jwk_dict: dict):
    """
    Extract public key from a JWK dict. Handles keys with x5c but no kty
    (e.g. from entity configurations that publish keys via x5c only).
    """
    if "kty" in jwk_dict:
        return key_from_jwk_dict(jwk_dict).public_key()
    # JWK has x5c but no kty - derive from certificate
    x5c = jwk_dict.get("x5c")
    if not x5c:
        raise ValueError("JWK must have either kty or x5c")
    der = base64.b64decode(x5c[0])
    cert = x509.load_der_x509_certificate(der)
    pub_key = cert.public_key()
    # Add kty so the JWK is valid for downstream consumers
    if isinstance(pub_key, rsa.RSAPublicKey):
        jwk_dict["kty"] = "RSA"
    elif isinstance(pub_key, ec.EllipticCurvePublicKey):
        jwk_dict["kty"] = "EC"
    elif isinstance(pub_key, (ed25519.Ed25519PublicKey, ed448.Ed448PublicKey)):
        jwk_dict["kty"] = "OKP"
    else:
        jwk_dict["kty"] = "RSA"  # fallback for unknown types
    return pub_key


def update_jwks_with_x5c(
    jwks: list,
    private_key: bytes,
    subject: str,
    is_ca_or_int: bool,
    path_length: Union[int, None] = None,
) -> dict:
    subject_data: dict = dict(
        X509_COMMON_NAME=urlparse(subject).hostname,
        # TODO: add COUNTRY_NAME, X509_STATE_OR_PROVINCE_NAME, X509_LOCALITY_NAME, X509_ORGANIZATION_NAME
        entity_id=subject
    )

    for i in jwks:
        i['x5c'] = X509Issuer(
            private_key = private_key,
            public_key = _public_key_from_jwk_dict(i),
            subject_data = subject_data,
            is_ca_or_int = is_ca_or_int,
            path_length = path_length
        ).x5c
    return jwks
