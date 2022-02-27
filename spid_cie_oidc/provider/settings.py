
from spid_cie_oidc.entity.utils import exp_from_now, iat_now

JWT_CLIENT_ASSERTION = {
    "iss": "http://rp-test/oidc/rp",
    "sub": "http://rp-test/oidc/rp",
    "iat": iat_now(),
    "exp": exp_from_now(33),
    "aud": ["https://rp.spid.agid.gov.it/auth"],
    "jti": "a72d5df0-2415-4c7c-a44f-3988b354040b",
}

PAYLOAD = {
    'client_id': 'http://127.0.0.1:8000/oidc/rp/',
    'sub': 'http://rp-test/oidc/rp',
    'iss': 'http://rp-test/oidc/rp',
    'response_type': 'code',
    'scope': 'openid',
    'code_challenge': 'qWJlMe0xdbXrKxTm72EpH659bUxAxw80',
    'code_challenge_method': 'S256',
    'nonce': 'MBzGqyf9QytD28eupyWhSqMj78WNqpc2',
    'prompt': 'consent login',
    'redirect_uri': 'https://rp.cie.it/callback1/',
    'acr_values': 'CIE_L1 CIE_L2',
    'claims': {
        'id_token': {
            'family_name': {'essential': True},
            'email': {'essential': True}
        },
        'userinfo': {
            'name': None,
            'family_name': None
        }
    },
    'state': 'fyZiOL9Lf2CeKuNT2JzxiLRDink0uPcd',
    "iat": iat_now(),
    "exp": exp_from_now(33),
    "aud": ["https://rp.spid.agid.gov.it/auth"],
    "jti": "a72d5df0-2415-4c7c-a44f-3988b354040b",
}

TA_STATMENT = {
    "sub": "http://127.0.0.1:8000/",
    "iss": "http://127.0.0.1:8000/",
    "iat": iat_now(),
    "exp": exp_from_now(33),
}
