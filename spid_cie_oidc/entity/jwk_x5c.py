from cryptojwt.jwk.jwk import key_from_jwk_dict

from django.utils import timezone
from spid_cie_oidc.entity.x509 import X509Issuer

from urllib.parse import urlparse


def update_jwks_with_x5c(
        jwks: list,
        private_key: bytes,
        subject: str,
        is_ca_or_int: bool,
        path_length: int = 0,
    ) -> dict:

    subject_data: dict = dict(
        X509_COMMON_NAME = urlparse(subject).hostname,
        # TODO: please add COUNTRY_NAME, X509_STATE_OR_PROVINCE_NAME, X509_LOCALITY_NAME, X509_ORGANIZATION_NAME
        entity_id = subject
    )
    
    for i in jwks:
        i['x5c'] = X509Issuer(
            private_key = private_key,
            public_key = key_from_jwk_dict(i).public_key(),
            subject_data = subject_data,
            is_ca_or_int = is_ca_or_int,
            path_length = path_length
        ).x5c
    return jwks
