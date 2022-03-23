# Openid Connect Relying Party Relying Party

A SPID/CIE implementation of a OpenID Connect Relying Party fully compliant to
AgID SPID guidelines and CIE id guidelines.

To date there are many libraries that enable OAuth2 and OIDC in a Django project,
this project instead born to be lightweight and simple.

What is available today represents the bare essentials to manage an authorization flow and requests
for token acquisition and user information, processing of attributes and identity reunification functions.

## Features

Regarding OAuth2

 - Authorization Code Grant: [rfc6749](https://tools.ietf.org/html/rfc6749#section-4.1)
 - PKCE: [rfc7636](https://tools.ietf.org/html/rfc7636)
 - [OAuth 2.0 Token Revocation](https://datatracker.ietf.org/doc/html/rfc7009)

Regarding OIDC

 - CodeFlowAuth: [openid-connect-core-1_0](https://openid.net/specs/openid-connect-core-1_0.html#CodeFlowAuth)
 - OIDC Federation 1.0: [openid-connect-federation-1_0](https://openid.net/specs/openid-connect-federation-1_0.html)
 - UserInfo endpoint: [UserInfo](https://openid.net/specs/openid-connect-core-1_0.html#UserInfo)

Regarding django user management

 - user attributes processing and rewriting from OAuth2 claims
 - reunification of digital identities

## General Settings Paramenters

Please see `example/relying_party/settingslocal.py` as example.

- `OIDCFED_DEFAULT_TRUST_ANCHOR` defines the default Trust Anchor.
- `OIDCFED_TRUST_ANCHORS` defines the allowed Trust Anchors. 
- `OIDCFED_IDENTITY_PROVIDERS` defines the list of OPs to enable in Trust Chain operations.

Example
````
OIDCFED_IDENTITY_PROVIDERS = {
  "spid": {
    "http://127.0.0.1:8000/oidc/op/" : OIDCFED_DEFAULT_TRUST_ANCHOR,
  },
  "cie": {
    "http://127.0.0.1:8002/oidc/op/" : OIDCFED_DEFAULT_TRUST_ANCHOR,
  }
}
````

- `RP_PREFS`: General informations, default parameters during authentication requests, like the `scope` attribute
- `RP_ATTR_MAP`: defines how oidc claims should be mapped to User model. You can even use a function to do rewrite or create new attributes (feel free to contribute with new processors in `processors.py`)
Example
    ````
    (
     {
        'func': 'spid_oidc_rp.processors.issuer_prefixed_sub',
        'kwargs': {'sep': '__'}
     },
    )
    ````
    Otherwise a simple mapping like this: `('firstname',),`
    Otherwise a multiple OR sequence: `('firstname', 'lastname'),`. This will check for the first occourrence
- `RP_PKCE_CONF`: function and general paramenters for PKCE creation

- `RP_PROVIDER_PROFILES`
Example
````
RP_PROVIDER_PROFILES = getattr(
    settings,
    "RP_PROVIDER_PROFILES",
    {
        "spid": {
            "authorization_request": {"acr_values": AcrValues.l2.value},
            "rp_metadata": RPMetadataSpid,
            "authn_response": AuthenticationResponse,
            "token_response": TokenResponse
        },
        "cie": {
            "authorization_request": {"acr_values": AcrValues.l2.value},
            "rp_metadata": RPMetadataCie,
            "authn_response": AuthenticationResponseCie,
            "token_response": TokenResponse
        },
    },
)
````
- `RP_USER_LOOKUP_FIELD`, which user attribute will be used to link to a preexisting account, example: `RP_USER_LOOKUP_FIELD = "fiscal_number"`.
- `RP_USER_CREATE`, if a newly logged user can be created, example: `RP_USER_CREATE = True`
- `RP_REQUEST_CLAIM_BY_PROFILE`

Example
````
RP_REQUEST_CLAIM_BY_PROFILE = {
    "spid": SPID_REQUESTED_CLAIMS,
    "cie": CIE_REQUESTED_CLAIMS,
}

SPID_REQUESTED_CLAIMS = getattr(
    settings,
    "RP_REQUIRED_CLAIMS",
    {
        "id_token": {
            "https://attributes.spid.gov.it/familyName": {"essential": True},
            "https://attributes.spid.gov.it/email": {"essential": True},
        },
        "userinfo": {
            "https://attributes.spid.gov.it/name": None,
            "https://attributes.spid.gov.it/familyName": None,
            "https://attributes.spid.gov.it/email": None,
            "https://attributes.spid.gov.it/fiscalNumber": None,
        },
    },
)

CIE_REQUESTED_CLAIMS = getattr(
    settings,
    "RP_REQUIRED_CLAIMS",
    {
        "id_token": {"family_name": {"essential": True}, "email": {"essential": True}},
        "userinfo": {
            "given_name": None,
            "family_name": None,
            "email": None,
        },
    },
)
````

- `LOGIN_REDIRECT_URL` url to which you are redirected after getting the user attributes  
Example
````
LOGIN_REDIRECT_URL = "/oidc/rp/echo_attributes"
````

`OIDCFED_ACR_PROFILES`, acr value required to OP Authentication Endpoint
Example
````
`OIDCFED_ACR_PROFILES` = AcrValues.l2.value
````

`RP_DEFAULT_PROVIDER_PROFILES`, default profile for OP

## OIDC Federation CLI

`fetch_openid_providers` build the Trust Chains for each `OIDCFED_IDENTITY_PROVIDERS`. Flag '-f' force trust chian renew even if is still valid.
````
examples/federation_authority/manage.py fetch_openid_providers --start -f

````
Flag '-f' force trust chian renew.

## Usage

Open your web browser and go to your debug server url, eg:

`http://localhost:8001/oidc/rp/begin?provider=http://127.0.0.1:8000/oidc/op/`

where `provider` is one of SPID/CIE OIDC providers.
Remember that you need a preexisting and valid Trust Chain, related
to that provider, before create an authorization request to it.

## Endpoints

### entity configuration (.well-known/openid-federation)

As inherited from [__spid_cie_oidc.entity__](docs/tecnhical_specifications/ENTITY.md).

### authorization

This endpoint is the starting point for OIDC SPID/CIE authentication.

The webpath is customizable in the `urls.py` file and by default it's
configured [here](https://github.com/peppelinux/spid-cie-oidc-django/blob/main/spid_cie_oidc/relying_party/urls.py#L13) 
and correspond to `spid_cie_oidc.relying_party.views.rp_begin.SpidCieOidcRpBeginView`.

The request is of type GET and supports the following parameters:

- __provider__, REQUIRED. To be enhanced with an http url corresponding to a subject id of a SPID/CIE OIDC Provider.
- __redirect_uri__, OPTIONAL. Selects one of the redirect_uri available in RP's metadata.
- __scope__, OPTIONAL. Selects one or more of the scopes, default is `openid`.
- __consent__, OPTIONAL. Sets SPID or CIE extended consent values.
- __trust_anchor__, OPTIONAL. Sets the Trust Anchor to resolve the Federation. Default is `settings.OIDCFED_DEFAULT_TRUST_ANCHOR`.
- __acr_values__, OPTIONAL.
- __profile__, OPTIONAL. Default: spid. Set (spid, cie)

### auth code redirect

This endpoint corresponds to the redirect uri where the auth code lands.

The webpath is customizable in the `urls.py` file and by default it's
configured [here](https://github.com/italia/spid-cie-oidc-django/blob/main/spid_cie_oidc/relying_party/urls.py#L19) 
and correspond to `spid_cie_oidc.relying_party.views.rp_callback.SpidCieOidcRpCallbackView`.

This endpoint accepts a request with this parameters:

- __code__, REQUIRED. Authorization code
- __state__, REQUIRED. State value enclosed in the authentication request
- __iss__, REQUIRED only for cie. Issuer identifier of the OP

This endpoint first call OP's token endpoint and, after getting the access token, it calls the OP's userinfo endpont.

The request to token endpoint is of type POST and supports the following parameters:

- __client_id__, REQUIRED. RP's client id
- __client_assertion__, REQUIRED. JWT signed by using the private key of the RP
- __client_assertion_type__, REQUIRED.
- __code__, REQUIRED. Authorization code recived from authorization endpoint
- __code_verifier__, REQUIRED
- __grant_type__, REQUIRED. Specified the way RP gets the OIDC-Core tokens. It may be "authorization_code" or "refresh_token"
- __refresh_token__, REQUIRED only if grant_type is refresh_token

The request to userinfo endpoint is of type GET and access token is sent using the authorization header field.


### logout

This endpoint calls the token revocation endpoint of the op.

The webpath is customizable in the `urls.py` file and by default it's
configured [here](https://github.com/italia/spid-cie-oidc-django/blob/main/spid_cie_oidc/relying_party/urls.py#L36) 
and correspond to `spid_cie_oidc.relying_party.views.rp_initiated_logout.oidc_rpinitiated_logout`.

The request contains user to logout

## SPID/CIE QAD and compliances tests

WiP
