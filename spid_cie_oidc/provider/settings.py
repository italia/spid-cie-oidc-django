

JWK = {
    'kty': 'RSA',
    'kid': 'oPeAc4EkuBL2wIM18PDdgB-l7uJhSft5Ca66w9ivB-Y',
    'n': 'mSZgB_75IAF8W9BEybYCVgjlneaqe-pHRc9391Kt-YY1d0YmvmjIwMI6mNqOtUdsKvqr1SLONc5l-N4qe2fP-Ky1_lT6Oqf4Dt-a89BEyMmj4xmVVUwgx9S5_upQgIp4HiZF92_ojd25HoGeLG460lEaXUT3P6ve0lBW-jw1cbUNIhAO9wgd-qReNRJJMFP_bzo-kPRXFw7YQg0U_SZJTPVqrtBB7tQYHdbLTmjR5rvvVe2jCI2bws5VKGXW15eQBkUhnJLGLFo30XTyNXWPQa7b3rb7RaNK8EYpWvxA5cUZTD2XqUFtUgZqQj6d-nCZteqi_jVGa3qg8iq5YDh5cw',
    'e': 'AQAB',
    'd': 'X-p12Gwq8I2dqg79Feuk-Ocnj8YIXgUzUBiIxOAGT7FrSOEpoLUVjgvXESZInGY3648FET50MaSrnrrdll5FFTRt4vSrpxLNu9r1O9_jRHFs7-105nAAU8b6Ghn8AxU194P26-otlrQXnXCGdMMwmcnrniB0TW9B5Swl3SDaQ_StTBy6BFzoAXJbNLUEcB_0PN1KHzGnwLsPJKISO5ZLXzyF37C97jWfCYTJ80-w8ie3GkCm8lnXwyzWwa2iVKDshvDooZYemnY6UsP_ob01sKE1-zJcvpRL5aku3uNRk0wE7TSIqKSmZ8pNpTdxsYHEEP3LMhvCrWS7_pH_o5JBIQ', 'p': 'yfd2gwPhgcWa4UPizUKVD1KM7YZP_TYmBa-BO5ejuneqMzYOIYeCJopvPnnB7L8i0rTnhGaqVuK5Ct961omat8p00c9pSHJGJG96LwYo7g5o9-BVyiBAofgqQ90rEQ4mhsNPmIAX9LNRICwQgUyTBt5sA7HV5jDeZ4FbjHI8ClE',
    'q': 'wh99z0c9QsjHOLO8klgCqFsWhGAydN7Aq05MkAg7RMVj1Wrof9Ma__hVaOrFUWGMd7vgPzvDdZfF8VjwQ-TcSUf5J5aIgvGTqYvQ0m4FKa45h_tonuTGhMHQnKLO1SbQWVVb22pEygeODjuLt-UV5zMRZdMP5GW_2RhONE-NkoM'
}

PAYLOAD = {
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
    'state': 'fyZiOL9Lf2CeKuNT2JzxiLRDink0uPcd'
}

METADATA = {
    'application_type': 'web',
    'client_registration_types': ['automatic'],
    'client_name': 'Name of this service called https://rp.example.it/spid',
    'contacts': ['ops@rp.example.it'],
    'grant_types': ['refresh_token', 'authorization_code'],
    'redirect_uris': ['https://rp.example.it/spid/callback'],
    'response_types': ['code'],
    'subject_type': 'pairwise',
    'jwks': [{'kty': 'RSA', 'e': 'AQAB', 'n': 'mSZgB_75IAF8W9BEybYCVgjlneaqe-pHRc9391Kt-YY1d0YmvmjIwMI6mNqOtUdsKvqr1SLONc5l-N4qe2fP-Ky1_lT6Oqf4Dt-a89BEyMmj4xmVVUwgx9S5_upQgIp4HiZF92_ojd25HoGeLG460lEaXUT3P6ve0lBW-jw1cbUNIhAO9wgd-qReNRJJMFP_bzo-kPRXFw7YQg0U_SZJTPVqrtBB7tQYHdbLTmjR5rvvVe2jCI2bws5VKGXW15eQBkUhnJLGLFo30XTyNXWPQa7b3rb7RaNK8EYpWvxA5cUZTD2XqUFtUgZqQj6d-nCZteqi_jVGa3qg8iq5YDh5cw', 'kid': 'oPeAc4EkuBL2wIM18PDdgB-l7uJhSft5Ca66w9ivB-Y'}]
}
