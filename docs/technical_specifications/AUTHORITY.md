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



#### Advanced entity listing endpoint

The advanced entity listing endpoint extends Listings endpoint.

The request MUST be an HTTP request using the GET method, an entity needs to know only the endpoint url.

Example of Advanced listing request: `http://127.0.0.1:8000/advanced_entity_listing/`


The response is a json object (content type: "application/json") in which for each entity the only REQUIRED claim is iat.
The entity's result set must have a descendant ordering with higher iat on top.

A response example: 
````
{
    "iss": "https://registry.spid.gov.it/",
    "iat": 1620050972,
    "entities": [
        {
            "https://rp.example.it/spid/": {
            "iat": 1588455866,
            },
            {
            "https://rp.another.it/spid/": {
            "iat": 1588455856,
            },
            {
            "https://rp.it/spid/": {
            "iat": 1588355866,
            },
        ... # many other entries
    ],
    "page": 1,
    "total_pages": 2,
    "total_entries": 189,
    "next_page_path": "/federation_adv_list/?page=2",
    "prev_page_path": ""
}
```` 




#### Resolve entity statement

An entity MAY use the resolve endpoint to fetch resolved metadata and trust marks for an entity as seen/trusted by the resolver. 

- `http://127.0.0.1:8000/resolve/?sub=http://127.0.0.1:8000/oidc/rp/&anchor=http://127.0.0.1:8000/&type=openid_relying_party&format=json`
- `http://127.0.0.1:8000/resolve/?sub=http://127.0.0.1:8000/oidc/op/&anchor=http://127.0.0.1:8000/`


#### trust mark status

This is to allow an entity to check whether a trust mark is still active or not. The query MUST be sent to the trust mark issuer.

- `http://127.0.0.1:8000/trust_mark_status/?id=https://www.spid.gov.it/openid-federation/agreement/op-public/&sub=http://127.0.0.1:8000/oidc/op`
- `http://127.0.0.1:8000/trust_mark_status/?trust_mark= ...`

