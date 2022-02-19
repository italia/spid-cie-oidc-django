# Federation Entity API

Retrieve all the RPs
````
FederationDescendant.objects.filter(
    metadata__openid_relying_party__isnull=False
)
````
