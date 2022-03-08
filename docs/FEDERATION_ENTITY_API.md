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

WiP

## TrustChain

WiP

## Retrieve all the RPs
````
FederationDescendant.objects.filter(
    metadata__openid_relying_party__isnull=False
)
````
