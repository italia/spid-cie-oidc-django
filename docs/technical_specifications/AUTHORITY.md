# Trust Anchor or Intermediary

Thins kind of Entity represents a trusted third party 
and below it must have other entities for which it provides an onboarding mechanism.

### Endpoints

All the endpoints are configured in the `urls.py` file of the project folder.

#### Fetch

All entities that are expected to publish entity statements about other entities MUST expose a Fetch endpoint.

Fetching entity statements is performed to collect entity statements one by one to gather trust chains.

To fetch an entity statement, an entity needs to know the identifier of the entity to ask (the issuer),
the fetch endpoint of that entity and the identifier of the entity that you want the statement to be about (the subject).

Example of FETCH request

- `http://127.0.0.1:8000/fetch/?sub=http://127.0.0.1:8000/oidc/rp/`
- `http://127.0.0.1:8000/fetch/?sub=http://127.0.0.1:8001/&format=json`

#### Listing

As described in the official specification
[here](https://openid.net/specs/openid-connect-federation-1_0.html#rfc.section.7.3.1).
It should be available only for __trust anchors__ and __intermediates__.

Lists all the descendant entities.

 - `http://127.0.0.1:8000/list/`
 - `http://127.0.0.1:8000/list/?is_leaf=false`
 - `http://127.0.0.1:8000/list/?is_leaf=true`
 - `http://127.0.0.1:8000/list/?type=openid_provider`

#### Resolve entity statement

An entity MAY use the resolve endpoint to fetch resolved metadata and trust marks for an entity as seen/trusted by the resolver. 

- `http://127.0.0.1:8000/resolve/?sub=http://127.0.0.1:8000/oidc/op/&anchor=http://127.0.0.1:8000/&format=json`
- `http://127.0.0.1:8000/resolve/?sub=http://127.0.0.1:8000/oidc/op/&anchor=http://127.0.0.1:8000/`

#### trust mark status

This is to allow an entity to check whether a trust mark is still active or not. The query MUST be sent to the trust mark issuer.

- `http://127.0.0.1:8000/trust_mark_status/?id=https://www.spid.gov.it/openid-federation/agreement/op-public/&sub=http://127.0.0.1:8000/oidc/op`
- `http://127.0.0.1:8000/trust_mark_status/?trust_mark= ...`

