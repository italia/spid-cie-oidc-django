# Openid Connect Relying Party Relying Party

A SPID/CIE implementation of a OpenID Connect Relying Party fully compliant to
AgID SPID guidelines and CIE id guidelines.

## General Settings Paramenters

- `OIDCFED_FEDERATION_TRUST_ANCHOR` defines the default Trust Anchor.
- `OIDCFED_FEDERATION_TRUST_ANCHORS` defines the allowed Trust Anchors. 
- `OIDCFED_IDENTITY_PROVIDERS` defines the list of OPs to enable in Trust Chain operations.

Example
````
OIDCFED_IDENTITY_PROVIDERS = [
    "http://127.0.0.1:8000/oidc/op/",
    "http://127.0.0.1:8002/"
]
````


## OIDC Federation CLI

`fetch_openid_providers` build the Trust Chains for each `OIDCFED_IDENTITY_PROVIDERS`. 
````
examples/federation_authority/manage.py fetch_openid_providers --start -f

````


## Endpoints

### entity configuration (.well-known/openid-federation)

As inherited from [__spid_cie_oidc.entity__](docs/tecnhical_specifications/ENTITY.md).

### authorization

This endpoint is the starting point for OIDC SPID/CIE authentication.

the webpath is customizable in the `urls.py` file and by default it's
configured [here](https://github.com/peppelinux/spid-cie-oidc-django/blob/main/spid_cie_oidc/relying_party/urls.py#L13) 
and correspond to `spid_cie_oidc.relying_party.views.SpidCieOidcRpBeginView`.

The request is of type GET and supports the following parameters:

- __provider__, REQUIRED. To be enhanced with an http url corresponding to a subject id of a SPID/CIE OIDC Provider.
- __redirect_uri__, OPTIONAL. Selects one of the redirect_uri available in RP's metadata.
- __scope__, OPTIONAL. Selects one or more of the scopes, default is `openid`.
- __consent__, OPTIONAL. Sets SPID or CIE extended consent values.
- __trust_anchor__, OPTIONAL. Sets the Trust Anchor to resolve the Federation. Default is `settings.OIDCFED_FEDERATION_TRUST_ANCHOR`

### auth code redirect

WiP

### logout

WiP

## SPID/CIE QAD and compliances tests

WiP
