# OIDC Federation 1.0 Entity

A Federation Entity is a service that meets the minimum requirements to integrate into OIDC Federation 1.0. This can be of the following types:

- Trust Anchor or Intermediary
- Relying Party
- Provider

### Endpoints

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


### API

See [The Entity API documentation](../FEDERATION_ENTITY_API.md).
