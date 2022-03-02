
from spid_cie_oidc.entity.utils import exp_from_now, iat_now

# TODO: we need factory function to get fresh now
IAT = iat_now()
EXP = exp_from_now()

REQUEST_OBJECT_PAYLOAD = {
    'client_id': 'http://127.0.0.1:8000/oidc/rp/',
    'sub': 'http://rp-test/oidc/rp',
    'iss': 'http://rp-test/oidc/rp',
    'response_type': 'code',
    'scope': ['openid'],
    'code_challenge': 'qWJlMe0xdbXrKxTm72EpH659bUxAxw80',
    'code_challenge_method': 'S256',
    'nonce': 'MBzGqyf9QytD28eupyWhSqMj78WNqpc2',
    'prompt': 'consent login',
    'redirect_uri': 'https://rp.cie.it/callback1/',
    'acr_values': ['https://www.spid.gov.it/SpidL1', 'https://www.spid.gov.it/SpidL2'],
    'claims': {
        'id_token': {
            'family_name': {'essential': True},
            'email': {'essential': True}
        },
        'userinfo': {
            'given_name': None,
            'family_name': None
        }
    },
    'state': 'fyZiOL9Lf2CeKuNT2JzxiLRDink0uPcd',
    'sub': "https://rp.cie.it/",
    'iss': "https://op.spid.agid.gov.it/",
    'aud': ["https://rp.spid.agid.gov.it/auth"],
    'iat': IAT,
    'exp': EXP,
    'jti': "a72d5df0-2415-4c7c-a44f-3988b354040b"
}

# METADATA = {
    # 'application_type': 'web',
    # 'client_registration_types': ['automatic'],
    # 'client_name': 'Name of this service called https://rp.example.it/spid',
    # 'contacts': ['ops@rp.example.it'],
    # 'grant_types': ['refresh_token', 'authorization_code'],
    # 'redirect_uris': ['https://rp.example.it/spid/callback'],
    # 'response_types': ['code'],
    # 'subject_type': 'pairwise',
    # 'jwks': [{'kty': 'RSA', 'e': 'AQAB', 'n': 'mSZgB_75IAF8W9BEybYCVgjlneaqe-pHRc9391Kt-YY1d0YmvmjIwMI6mNqOtUdsKvqr1SLONc5l-N4qe2fP-Ky1_lT6Oqf4Dt-a89BEyMmj4xmVVUwgx9S5_upQgIp4HiZF92_ojd25HoGeLG460lEaXUT3P6ve0lBW-jw1cbUNIhAO9wgd-qReNRJJMFP_bzo-kPRXFw7YQg0U_SZJTPVqrtBB7tQYHdbLTmjR5rvvVe2jCI2bws5VKGXW15eQBkUhnJLGLFo30XTyNXWPQa7b3rb7RaNK8EYpWvxA5cUZTD2XqUFtUgZqQj6d-nCZteqi_jVGa3qg8iq5YDh5cw', 'kid': 'oPeAc4EkuBL2wIM18PDdgB-l7uJhSft5Ca66w9ivB-Y'}]
# }
