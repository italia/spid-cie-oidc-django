from cryptojwt.jwk.jwk import key_from_jwk_dict
from django.core.exceptions import ValidationError
from .jwks import serialize_rsa_key
from typing import Union

import json


def validate_public_jwks(values: Union[dict, list]):
    if isinstance(values, dict):
        values = [values]
    try:
        for jwk_dict in values:
            _k = key_from_jwk_dict(jwk_dict)
            if _k.private_key():
                _pub = serialize_rsa_key(_k.public_key())
                raise ValidationError(
                    f"This JWK is is private {json.dumps(jwk_dict)}. "
                    f"It MUST be public instead, like this: {json.dumps([_pub])}."
                )
    except Exception as e:
        raise ValidationError(f"Not valid: {e}")


def validate_private_jwks(values: Union[dict, list]):
    if isinstance(values, dict):
        values = [values]
    try:
        for jwk_dict in values:
            _k = key_from_jwk_dict(jwk_dict)
            if not _k.private_key():
                raise ValidationError(f"Can't extract a private JWK from {jwk_dict}")
    except Exception as e:
        raise ValidationError(f"Not valid: {e}")
