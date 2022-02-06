# spid-cie-oidc-relying-party

OpenID Connect 1.0 is a simple identity layer on top of the OAuth 2.0 protocol.
It enables Clients to verify the identity of the End-User based on the authentication
performed by an Authorization Server, as well as to obtain basic profile information
about the End-User in an interoperable and REST-like manner.

## Introduction

spid-cie-oidc-relying-party enables OIDC Authentication in your django project.

To date there are many libraries that enable OAuth2 and OIDC in a Django project,
this project instead born to be lightweight and simple, compliant with
standards and in line with what defined in [OIDC SPID](https://docs.italia.it/AgID/documenti-in-consultazione/lg-openidconnect-spid-docs/it/bozza/index.html)
guidelines.

What is available today represents the bare essentials to manage an authorization flow and requests
for token acquisition and user information, processing of attributes and identity reunification functions.


## Features

Regarding OAuth2

 - Authorization Code Grant: [rfc6749](https://tools.ietf.org/html/rfc6749#section-4.1)
 - PKCE: [rfc7636](https://tools.ietf.org/html/rfc7636)

Regarding OIDC

 - CodeFlowAuth: [openid-connect-core-1_0](https://openid.net/specs/openid-connect-core-1_0.html#CodeFlowAuth)
 - Discovery Provider: [openid-connect-core-1_0](https://openid.net/specs/openid-connect-core-1_0.html#SelfIssuedDiscovery)
 - UserInfo endpoint: [UserInfo](https://openid.net/specs/openid-connect-core-1_0.html#UserInfo)
 - RP Initiated logout: [openid-connect-rpinitiated-1_0](https://openid.net/specs/openid-connect-rpinitiated-1_0.html)

Regarding django user management

 - user attributes processing and rewriting from OAuth2 claims
 - reunification of digital identities

Then start the demo server
````
pip install -r requirements.txt
cd example
./manage.py migrate
./manage.py createsuperuser
./manage.py runserver 0.0.0.0:8888
````

Open your web browser and go to your debug server url, eg:

`http://localhost:8888/oidc/rp/begin?issuer_id=op_test`

where `issuer_id` is one of SPID/CIE OIDC providers.


## Settings

Please see `example/example/spid_oidc_rp_settings.py` as example.

- `RP_PREFS`: General informations, default parameters during authentication requests, like the `scope` attribute
- `RP_ATTR_MAP`: defines how oidc claims should be mapped to User model. You can even use a function to do rewrite or create new attributes (feel free to contribute with new processors in `processors.py`)
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

TODO:
- `user_lookup_field`: the django user field, where the reunification lookup happens, eg: `('username'),`
- `user_create`: creates a new user if the reunification lookup fails


## Tests

Tests needs that a debug server have to be executed, this is for simulate the entire auth code flow as it's real.
spid-django-oidc have an application called `op_test` that's involved in testing.

So, first of all execute the test server as follow
````
./manage.py runserver 0.0.0.0:8888
````

Then run the tests in a separate shell with `./manage.py test`.

Code Coverage
````
pip install coverage
coverage erase; coverage run ./manage.py test ; coverage report -m
````
