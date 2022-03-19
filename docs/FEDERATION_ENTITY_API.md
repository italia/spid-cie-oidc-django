# Federation Entity API

Federation Entity is the application where we have all the tools to configure our entity and
establish the trust to other third party entities.

An entity can be one of:

 - openid_relying_party
 - openid_provider
 - federation_entity (trust anchor or intermediary)

To create an OIDC Federation you have to configure a Trust Anchor first.
Read [FEDERATION_AUTHORITY](FEDERATION_AUTHORITY.md) to see how to do it.

## EntityConfiguration

__spid_cie_oidc.entity.statements__ contains all we need to deal with entity statements, configurations and trust marks.
The starting point is just the entity configuration and from this we created the class EntityConfiguration" 
[here](https://github.com/italia/spid-cie-oidc-django/blob/main/spid_cie_oidc/entity/statements.py#L132).

__EntityConfiguration__ takes a jwt, previously fetched with the function get_entity_configurations, also available in statements.py.
It also can takes `filter_by_allowed_trust_marks` as a list of allowed trust mark needed for validate the entity configuration.

Once we have an EntityConfiguration object we can use its methods to validate it in many several ways:

- __validate_by_itself__, validate the self-signed JWT
- __validate_by_allowed_trust_marks__, if passed in its object constructor it will look for at least one allowed trust mark.
It will fetches the trust anchor entity configuation and trust mark issuers entity configurations to achieve this.
- __validate_by_superior_statement__, fetches the entity statement of its superiors and validate itself.
- __validate_descendant_statement__, if a entity statement of a descendant of itself is submitted, it also validate it

## TrustChain

The TrustChain object is available [here](https://github.com/italia/spid-cie-oidc-django/blob/main/spid_cie_oidc/entity/trust_chain.py),
the evaluate operations [here](https://github.com/italia/spid-cie-oidc-django/blob/main/spid_cie_oidc/entity/trust_chain_operations.py).

To evaluate a TrustChain we need at least of three things:

- __subject identifier__ of the entity to which we want to establish the trust, the leaf.
- __trust_anchor__, subject identifier of the Federation authority that represent the Federation,
the root of the trust and the point of arrival, the final destination, of the path of trust.
- __metadata_type__, which kind of metadata we want to export from the trust chain, if openid provider or relying party.
The final metadata will be combined with the metadata policy of the superiors statements.
- __required_trust_marks__, which trust marks are required to start a metadata discovery on the subject of the trust chain.
At least one MUST be present as valid in the entity configuration of the subject. The validation of the trust mark JWS must be done
with one of the the public federation JWK publiched in the Trust Anchor entity configuration. The Trust Anchor MAY enable many trust marks issuers.
In this case the verifier MUST fetch all the entity configuration of the issuers related to the trust mark available in the entity configuration of the
subject of the Trust chain.

And implementation proposal is what we have in the function called `get_or_create_trust_chain` where a
verifier submits the previous argument and get a valid trust chain if available o a new one.

In each trust chain object we have a final metadata, as the result of the applied metadata policy published by the trust anchor in relation
of its descendants.

## Retrieve all the RPs

A Federation entity like a Trust anchor or Intermediary can get all its descentants of a type
from its database, using a Django ORM query. Eg:

````
FederationDescendant.objects.filter(
    metadata__openid_relying_party__isnull=False
)
````

### Resolve entity statements

See [Authority specs](technical_specifications/AUTHORITY.md).
