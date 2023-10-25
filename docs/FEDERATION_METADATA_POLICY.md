# Federation Metadata Policy

We use [Roland's implementation](https://github.com/rohe/fedservice/blob/master/src/fedservice/entity_statement/policy.py) for appling metadata policy and retrieve a final metadata.

#### Example
Enter in your project shell
````
./manage.py shell
````

Then

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
    "scope": {
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
 'scope': ['openid']}
````

Another example with OpenID Connect Provider
````
md = {
  "authorization_endpoint":"https://idp.it/openid/authorization",
  "token_endpoint": "https://idp.it/openid/token",
  "userinfo_endpoint": "https://idp.it/openid/userinfo",
  "introspection_endpoint": "https://idp.it/openid/introspection",
  "claims_parameter_supported": True,
  "contacts": ["ops@https://idp.it"],
  "client_registration_types_supported": ["automatic"],
  "request_authentication_methods_supported": {
     "ar": [
       "request_object"
  ]},
  "acr_values_supported": [
     "https://www.spid.gov.it/SpidL1",
     "https://www.spid.gov.it/SpidL2",
     "https://www.spid.gov.it/SpidL3"
   ],
  "claims_supported": [
        "https://attributes.eid.gov.it/spid_code",
        "given_name",
        "family_name",
        "place_of_birth",
        "birthdate",
        "gender",
        "https://attributes.eid.gov.it/company_name",
        "https://attributes.eid.gov.it/registered_office",
        "https://attributes.eid.gov.it/fiscal_number",
        "https://attributes.eid.gov.it/company_fiscal_number",
        "https://attributes.eid.gov.it/vat_number",
        "document_details",
        "phone_number",
        "email",
        "https://attributes.eid.gov.it/e_delivery_service",
        "https://attributes.eid.gov.it/eid_exp_date",
        "address"
   ],
  "grant_types_supported": [
    "authorization_code",
    "refresh_token"
  ],
  "id_token_signing_alg_values_supported": [
    "RS256",
    "ES256"
  ],
  "issuer": "https://idp.it",
  "jwks_uri": "https://idp.it/openid/jwks.json",
 "scopes_supported": [
   "openid",
   "offline_access"
 ],
  "logo_uri":  "https://idp.it/statics/logo.svg",
  "organization_name": "SPID OIDC identity provider",
  "op_policy_uri":  "https://idp.it/en/website/legal-information",
  "request_parameter_supported": True,
  "request_uri_parameter_supported": True,
  "require_request_uri_registration": True,
  "response_types_supported": ["code"],
  "subject_types_supported": ["pairwise", "public"],
  "token_endpoint_auth_methods_supported": ["private_key_jwt"],
          "token_endpoint_auth_signing_alg_values_supported": [
            "RS256",
            "RS384",
            "RS512",
            "ES256",
            "ES384",
            "ES512"
          ],
          "userinfo_encryption_alg_values_supported": [
            "RSA-OAEP",
            "RSA-OAEP-256",
            "ECDH-ES",
            "ECDH-ES+A128KW",
            "ECDH-ES+A192KW",
            "ECDH-ES+A256KW"
          ],
         "userinfo_encryption_enc_values_supported": [
            "A128CBC-HS256",
            "A192CBC-HS384",
            "A256CBC-HS512",
            "A128GCM",
            "A192GCM",
            "A256GCM"
          ],
         "userinfo_signing_alg_values_supported": [
            "RS256",
            "RS384",
            "RS512",
            "ES256",
            "ES384",
            "ES512"
         ],
"request_object_encryption_alg_values_supported": [
    "RSA-OAEP",
    "RSA-OAEP-256",
    "ECDH-ES",
    "ECDH-ES+A128KW",
    "ECDH-ES+A192KW",
    "ECDH-ES+A256KW"
   ],
 "request_object_encryption_enc_values_supported": [
    "A128CBC-HS256",
    "A192CBC-HS384",
    "A256CBC-HS512",
    "A128GCM",
    "A192GCM",
    "A256GCM"
  ],
  "request_object_signing_alg_values_supported": [
    "RS256",
    "RS384",
    "RS512",
    "ES256",
    "ES384",
    "ES512"
  ]
}

policy = {'contacts': {'add': ['ops@idp.it']},
   'organization_name': {'value': 'SPID OIDC Identity Provider'},
   'subject_types_supported': {'subset_of': ['pairwise']}}

apply_policy(md, policy)

````
