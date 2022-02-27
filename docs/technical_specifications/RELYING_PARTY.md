# Openid Connect Relying Party Relying Party

A SPID/CIE implementation of a OpenID Connect Relying Party fully compliant to
AgID SPID guidelines and CIE id guidelines.

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



### auth code redirect

WiP

### logout

WiP

## SPID/CIE QAD and compliances tests

WiP
