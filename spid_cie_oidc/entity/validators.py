import json
from typing import Union

from cryptojwt.jwk.jwk import key_from_jwk_dict
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from spid_cie_oidc.provider.settings import (
    OIDCFED_DEFAULT_PROVIDER_PROFILE,
    OIDCFED_PROVIDER_PROFILES
)
from spid_cie_oidc.relying_party.settings import (
    RP_DEFAULT_PROVIDER_PROFILES,
    RP_PROVIDER_PROFILES
)

from .jwks import serialize_rsa_key
from .settings import (
    ENCRYPTION_ALG_VALUES_SUPPORTED,
    ENCRYPTION_ENC_SUPPORTED,
    ENTITY_TYPES,
    SIGNING_ALG_VALUES_SUPPORTED
)


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


def validate_metadata_algs(metadata: dict):
    amap = dict(
        id_token_signing_alg_values_supported = SIGNING_ALG_VALUES_SUPPORTED,
        id_token_encryption_alg_values_supported = ENCRYPTION_ALG_VALUES_SUPPORTED,
        id_token_encryption_enc_values_supported = ENCRYPTION_ENC_SUPPORTED,
        token_endpoint_auth_signing_alg_values_supported = SIGNING_ALG_VALUES_SUPPORTED,
        userinfo_encryption_alg_values_supported = ENCRYPTION_ALG_VALUES_SUPPORTED,
        userinfo_encryption_enc_values_supported = ENCRYPTION_ENC_SUPPORTED,
        userinfo_signing_alg_values_supported = SIGNING_ALG_VALUES_SUPPORTED,
        request_object_encryption_alg_values_supported = ENCRYPTION_ALG_VALUES_SUPPORTED,
        request_object_encryption_enc_values_supported = ENCRYPTION_ENC_SUPPORTED,
        request_object_signing_alg_values_supported = SIGNING_ALG_VALUES_SUPPORTED,
    )
    if metadata.get("openid_provider", None):
        md = metadata["openid_provider"]
        for k, v in amap.items():
            if k in md:
                for alg in md[k]:
                    if alg not in v:
                        raise ValidationError(
                            f"{k} has an unsupported value {alg}. "
                            f"Supported algs are {v}"
                        )


def validate_entity_metadata(value):
    status = False
    for i in ENTITY_TYPES:
        if i in value:
            status = True
    if not status:
        raise ValidationError(
            _(f'Need to specify one of {", ".join(ENTITY_TYPES)}')
        )
    if "openid_provider" in value:
        schema = OIDCFED_PROVIDER_PROFILES[OIDCFED_DEFAULT_PROVIDER_PROFILE]
        try:
            schema["op_metadata"](**value["openid_provider"])
        except Exception as e:
            raise ValidationError(
                f"OP metadata fail {e}. "
            )
    if "openid_relying_party" in value:
        schema = RP_PROVIDER_PROFILES[RP_DEFAULT_PROVIDER_PROFILES]
        try:
            schema["rp_metadata"](**value["openid_relying_party"])
        except Exception as e:
            raise ValidationError(
                f"RP metadata fail {e}. "
            )


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
