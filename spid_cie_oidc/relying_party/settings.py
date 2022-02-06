RP_PREFS = {
    'application_name': 'that_fancy_rp',
    'application_type': 'web',
    'contacts': ['ops@example.com'],
    'response_types': ['code'],
    'scope': ['openid', 'offline_access'],
    'token_endpoint_auth_method': [
        'private_key_jwt'
    ]
}


RP_ATTR_MAP = {
    'username': (
                 {
                    'func': 'spid_cie_oidc.relying_party.processors.issuer_prefixed_sub',
                    'kwargs': {'sep': '__'}
                 },
                ),
    'first_name': ('firstname',),
    'last_name': ('lastname',),
    'email': ('email',),
}


RP_PKCE_CONF = {
    'function': 'spid_cie_oidc.relying_party.utils.get_pkce',
    'kwargs': {
        'code_challenge_length': 64,
        'code_challenge_method': 'S256'
    }
}


RP_PROVIDERS = {
    'op_test': {
        'issuer': 'http://localhost:8888',
        'discovery_url': 'http://localhost:8888/oidc/op/openid-configuration',
        'client_preferences': RP_PREFS,
        'client_id': 'that-id',
        'client_secret': 'that-secret',
        'redirect_uris': ['http://localhost:8888/callback'],
        'httpc_params':  {'verify': False},
        'add_ons': {
            'pkce': RP_PKCE_CONF
        },
        'user_attributes_map': RP_ATTR_MAP,
        'user_lookup_field': ('username'),
        'user_create': True,
        'login_redirect_url': '/echo_attributes'
    }
}
