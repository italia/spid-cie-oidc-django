# Federation Metadata Policy

We use [Roland's implementation](https://github.com/rohe/fedservice/blob/master/src/fedservice/entity_statement/policy.py) for appling metadata policy and retrieve a final metadata.

Example

````
from spid_cie_oidc.entity.policy import apply_policy

metadata = {
    "application_type": "web",
    "client_registration_types": ["automatic"],
    "client_name": "Name of this service called https://rp.example.it/spid",
    "contacts": ["ops@rp.example.it"],
    "grant_types": ["refresh_token", "authorization_code"],
    "jwks": {
        "kty": "RSA",
        "n": "1cE1PyQiBkmwO4TT30HGUwegdPZ9iKvuwQezUYOe8LqGol_6sUgxAf67_KbAeP1PMrmGH6d-AgNIT2Taa0OAtqyRUTLhG8rl7gT3_Jzwt2mOJu2JI4MfWcQxa-ZtzM8PPr7JUzWUzhHO7Nb1MfBm_fqB20cRcHOS_fvu3PqY-C-t33z3JYeDD_PsvSs2-WLlUiMDf9ILp0rVatF4GTPwvEp7VLCqCf1lLSLIxuuTVI0sc1j3xPbyv4MO_33fTmoAOVDmkUnhi2igLgw_tjc2-iu_4-r2qsKbotGiTu6y1RQrHc8xcrQmfqJ8FUwqAcpgQnlsekEHc6lWx9262Anobw",
        "e": "AQAB",
        "kid": "2C3zbeQjgx3jk-CHSqK3pLhdPeV9Fn5eSBPMNUp7vQk",
    },
    "redirect_uris": ["https://rp.example.it/spid/callback"],
    "response_types": ["code"],
    "subject_type": "pairwise",
}

policy = {
    "scopes": {
        "default": ["openid"],
        "superset_of": ["openid"],
        "subset_of": ["openid", "offline_access", "profile", "email"],
    },
    "contacts": {"add": ["ciao@email.it"]},
}

apply_policy(metadata, policy)
````

`apply_policy()` returns the final metadata, as follows

````
{'application_type': 'web',
 'client_registration_types': ['automatic'],
 'client_name': 'Name of this service called https://rp.example.it/spid',
 'contacts': ['ops@rp.example.it', 'ciao@email.it'],
 'grant_types': ['refresh_token', 'authorization_code'],
 'jwks': {'kty': 'RSA',
  'n': '1cE1PyQiBkmwO4TT30HGUwegdPZ9iKvuwQezUYOe8LqGol_6sUgxAf67_KbAeP1PMrmGH6d-AgNIT2Taa0OAtqyRUTLhG8rl7gT3_Jzwt2mOJu2JI4MfWcQxa-ZtzM8PPr7JUzWUzhHO7Nb1MfBm_fqB20cRcHOS_fvu3PqY-C-t33z3JYeDD_PsvSs2-WLlUiMDf9ILp0rVatF4GTPwvEp7VLCqCf1lLSLIxuuTVI0sc1j3xPbyv4MO_33fTmoAOVDmkUnhi2igLgw_tjc2-iu_4-r2qsKbotGiTu6y1RQrHc8xcrQmfqJ8FUwqAcpgQnlsekEHc6lWx9262Anobw',
  'e': 'AQAB',
  'kid': '2C3zbeQjgx3jk-CHSqK3pLhdPeV9Fn5eSBPMNUp7vQk'},
 'redirect_uris': ['https://rp.example.it/spid/callback'],
 'response_types': ['code'],
 'subject_type': 'pairwise',
 'scopes': ['openid']}
````
