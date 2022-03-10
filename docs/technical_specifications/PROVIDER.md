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

WiP

### token

WiP

### token introspection

WiP

### token revocation

WiP

### userinfo endpoint

WiP


## SPID/CIE QAD and compliances tests

WiP
