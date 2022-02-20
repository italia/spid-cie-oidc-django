# OIDC Federation 1.0 Entity

A Federation Entity is a service that meets the minimum requirements to integrate into OIDC Federation 1.0. This can be of the following types:

- Trust Anchor or Intermediary
- Relying Party
- Provider


## Trust Anchor or Intermediary

Thins kind of Entity represents a trusted third party 
and below it must have other entities for which it provides an onboarding mechanism.

### Endpoints:

All the endpoints are configured in the `urls.py` file of the project folder.

#### entity configuration

It's an endpoint that by default corresponds to this webpath: __.well-known/openid-federation__.
This provides the Entity Configuration in signed JWT format.
This endpoint MUST be available for __trust anchors__, __providers__ and __relying parties__.

You can manage additional custom paths for your descendants if you publish the Entity Configuration on their behalf.

`?format=json` will release a json for debug purpose. A prefix can be configured in global settings file with parameter `OIDC_PREFIX`.

Examples of requests to this endpoint are:

- `http://127.0.0.1:8000/.well-known/openid-federation?format=json`
- `http://127.0.0.1:8000/.well-known/openid-federation`

#### fetch

All entities that are expected to publish entity statements about other entities MUST expose a Fetch endpoint.

Fetching entity statements is performed to collect entity statements one by one to gather trust chains.

To fetch an entity statement, an entity needs to know the identifier of the entity to ask (the issuer),
the fetch endpoint of that entity and the identifier of the entity that you want the statement to be about (the subject).

Example of FETCH request

- `http://127.0.0.1:8000/fetch/?sub=http://127.0.0.1:8000/oidc/rp/`
- `http://127.0.0.1:8000/fetch/?sub=http://127.0.0.1:8001/&format=json`

#### listing

As described in the official specification
[here](https://openid.net/specs/openid-connect-federation-1_0.html#rfc.section.7.3.1).
It should be available only for __trust anchors__ and __intermediates__.

Lists all the descendant entities.

 - `http://127.0.0.1:8000/list/`
 - `http://127.0.0.1:8000/list/?is_leaf=false`
 - `http://127.0.0.1:8000/list/?is_leaf=true`

#### resolve entity statement

WiP

#### trust mark status

WiP
