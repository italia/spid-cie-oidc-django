# __Openid Connect Provider__ Identity Provider with additional test suite.

A SPID/CIE implementation of a OpenID Connect Provider fully compliant to
AgID SPID guidelines and CIE id guidelines.

## General settings

All the Provider settings paramenter are available at
[spid_cie_oidc.provider.settings](spie_cie_oidc/provider/settings.py) and
can be inherited in the general settings file of your project.


`OIDCFED_PROVIDER_PROFILES` supported profiles.
````
OIDCFED_PROVIDER_PROFILES = getattr(
    settings,
    'OIDCFED_PROVIDER_PROFILES',
    {
        "spid": {
            "authentication_request": AuthenticationRequestSpid,
        },
        "cie": {
            "authentication_request": AuthenticationRequestCie,
        }
    }
)
````

````
OIDCFED_DEFAULT_PROVIDER_PROFILE = getattr(
    settings,
    "OIDCFED_PROVIDER_PROFILE",
    "Spid"
)
````

`OIDCFED_PROVIDER_MAX_REFRESH = 1` How many times a token can be refreshed.


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

## SPID/CIE QAD and compliances tests

WiP
