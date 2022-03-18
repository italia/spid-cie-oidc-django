# __Openid Connect Provider__ Identity Provider with additional test suite.

A SPID/CIE implementation of a OpenID Connect Provider fully compliant to
AgID SPID guidelines and CIE id guidelines.

## General settings

All the Provider settings paramenter are available at
[spid_cie_oidc.provider.settings](spie_cie_oidc/provider/settings.py) and
can be inherited in the general settings file of your project.

- `OIDCFED_PROVIDER_PROFILES_MEDIA` 
Example
````
OIDCFED_PROVIDER_PROFILES_MEDIA = getattr(
    settings,
    "OIDCFED_PROVIDER_PROFILES_MEDIA",
    {
        "spid": {
            "logo": "svg/spid-logo-c-lb.svg"
        },
        "cie": {
            "logo": "images/logo-cie.png"
        },
    },
)
````

- `OIDCFED_PROVIDER_PROFILES` supported profiles.
Example
````
OIDCFED_PROVIDER_PROFILES = getattr(
    settings,
    "OIDCFED_PROVIDER_PROFILES",
    {
        "spid": {
            "authorization_request": AuthenticationRequestSpid,
            "op_metadata": OPMetadataSpid,
            "authorization_code": TokenAuthnCodeRequest,
            "refresh_token": TokenRefreshRequest,
            "revocation_request": RevocationRequest,
            "introspection_request" : IntrospectionRequest,
        },
        "cie": {
            "authorization_request": AuthenticationRequestCie,
            "op_metadata": OPMetadataCie,
            "authorization_code": TokenAuthnCodeRequest,
            "refresh_token": TokenRefreshRequest,
            "revocation_request": RevocationRequest,
            "introspection_request" : IntrospectionRequest,
        },
    },
)
````
- `OIDCFED_DEFAULT_PROVIDER_PROFILE`
Example
````
OIDCFED_DEFAULT_PROVIDER_PROFILE = getattr(
    settings,
    "OIDCFED_PROVIDER_PROFILE",
    "Spid"
)
````

- `OIDCFED_PROVIDER_MAX_REFRESH` How many times a token can be refreshed.

- `OIDCFED_PROVIDER_ATTRIBUTES_SPID_MAP` map of attributes for a spid provider
- `OIDCFED_PROVIDER_ATTRIBUTES_CIE_MAP` map of attributes for a cie provider
- `OIDCFED_PROVIDER_ATTRIBUTES_MAP` map of all provider attributes

- `OIDCFED_PROVIDER_PROFILES_ID_TOKEN_CLAIMS` claims that can be requested to token endpoint
Example
````
OIDCFED_PROVIDER_PROFILES_ID_TOKEN_CLAIMS = dict(
    spid = dict(),
    cie = OIDCFED_PROVIDER_ATTRIBUTES_CIE_MAP
)
````

-`OIDCFED_PROVIDER_SALT`
Example
````
OIDCFED_PROVIDER_SALT = getattr(settings, "OIDCFED_PROVIDER_SALT", "CHANGEME")
````

- `OIDCFED_PROVIDER_HISTORY_PER_PAGE`
Example
````
OIDCFED_PROVIDER_HISTORY_PER_PAGE = getattr(settings, "OIDCFED_PROVIDER_HISTORY_PER_PAGE", 50)
````

- `OIDCFED_PROVIDER_AUTH_CODE_MAX_AGE` lifetime of validity of an auth code
Example
````
OIDCFED_PROVIDER_AUTH_CODE_MAX_AGE = getattr(
    settings,
    "OIDCFED_PROVIDER_AUTH_CODE_MAX_AGE",
    10
)
````

- `OIDCFED_PROVIDER_PROFILES_DEFAULT_ACR` default acr value that is satisfied by the OP in the Authentication Request
Example
````
OIDCFED_PROVIDER_PROFILES_DEFAULT_ACR = dict(
    spid = AcrValuesSpid.l2.value,
    cie = AcrValuesCie.l2.value
)
````

- `OIDCFED_ATTRNAME_I18N`

## Endpoints

the webpath where the provider serve its features are the followins.

### entity configuration (.well-known/openid-federation)

As inherited from [__spid_cie_oidc.entity__](docs/tecnhical_specifications/ENTITY.md).

### authorization

The webpath is customizable in the `urls.py` file and by default it's
configured [here](https://github.com/italia/spid-cie-oidc-django/blob/dev/spid_cie_oidc/provider/urls.py#L16) 
and correspond to `spid_cie_oidc.provider.views.AuthzRequestView`.

The Authorization Endpoint support the use of the HTTP GET and POST methods.

An exemple of accepted rquest is [heare](https://github.com/italia/spid-cie-oidc-django/blob/dev/spid_cie_oidc/onboarding/tests/authn_request_settings.py#L30)

For Spid profile only 'userinfo' claims are accepted, for CIE profile both 'userinfo' and 'id_token'.

In the case of successful user authentication, the response contains the following parameters:

- __code__, REQUIRED. Authorization code.
- __state__, REQUIRED. State value enclosed in the authentication requests.
- __iss__, REQUIRED for CIE, OPTIONAL for Spid. Issuer identifier of the OP.
- __scope__, REQUIRED if the scopes are different from those required by RP.

### token

The webpath is customizable in the `urls.py` file and by default it's
configured [here](https://github.com/italia/spid-cie-oidc-django/blob/dev/spid_cie_oidc/provider/urls.py#L27) 
and correspond to `spid_cie_oidc.provider.views.TokenEndpoint`.

Token endpoint support the use only of the HTTP POST method and accepts as grant_type both 'authorization_code' and 'refresh_token'.

### token introspection

The webpath is customizable in the `urls.py` file and by default it's
configured [here](https://github.com/italia/spid-cie-oidc-django/blob/dev/spid_cie_oidc/provider/urls.py#L42) 
and correspond to `spid_cie_oidc.provider.views.IntrospectionEndpoint`.

Introspection endpoint support the use only of the HTTP POST method, an example of acceptet request is [here](https://github.com/italia/spid-cie-oidc-django/blob/dev/spid_cie_oidc/onboarding/tests/introspection_request_settings.py#L3)

In the response the only REQUIRED attribute is __active__, boolean indicator of whether the presented token is currently active.

### token revocation

The webpath is customizable in the `urls.py` file and by default it's
configured [here](https://github.com/italia/spid-cie-oidc-django/blob/dev/spid_cie_oidc/provider/urls.py#L37) 
and correspond to `spid_cie_oidc.provider.views.RevocationEndpoint`.

Revocation endpoint support the use only of the HTTP POST method.

In case of successful token invalidation, responds with an HTTP 200 code.

### userinfo

The webpath is customizable in the `urls.py` file and by default it's
configured [here](https://github.com/italia/spid-cie-oidc-django/blob/dev/spid_cie_oidc/provider/urls.py#L32) 
and correspond to `spid_cie_oidc.provider.views.UserInfoEndpoint`.

The UserInfo Endpoint returns an encrypthed jwt of the user claims.

### Login history page

![OIDC Provider login history](docs/images/provider_login_history.png)
_The user can consult the history of his accesses and also can revoke the access tokens for selected RPs._

## SPID/CIE QAD and compliances tests

WiP
