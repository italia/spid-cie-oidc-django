## Create a Trust Anchor

We can create our entity though the Admin backend or via API.
In the following example we create a Trust Anchor Entity.

The JWKS if not submitted will be created automatically.

````
from spid_cie_oidc.entity.models import *

TA_SUB = "http://testserver/"
FA_METADATA = {
    "federation_entity": {
        "contacts": ["ops@localhost"],
        "federation_api_endpoint": f"{TA_SUB}/fetch",
        "homepage_uri": f"{TA_SUB}",
        "name": "example TA",
    }
}
TM_ISSUERS = {
    "https://www.spid.gov.it/certification/rp/public": [
        TA_SUB,
        "https://public.intermediary.spid.it",
    ],
    "https://www.spid.gov.it/certification/rp/private": [
        TA_SUB,
        "https://private.other.intermediary.it",
    ],
    "https://sgd.aa.it/onboarding": ["https://sgd.aa.it"],
}
FA_CONSTRAINTS = {"max_path_length": 1}

ta_conf_data = dict(
    sub=TA_SUB,
    metadata=FA_METADATA,
    constraints=FA_CONSTRAINTS,
    is_active=1,
    trust_marks_issuers=TM_ISSUERS,
)

FederationEntityConfiguration.objects.create(**ta_conf_data)
````

Using different kind of metadata we can create OpenID Relying Parties or Providers.
Just rememeber, for these latter, to add also the authority_hints value as follow

````
authority_hints = ["http://testserver/"]
````

## Register descendants

see [unit tests](https://github.com/peppelinux/spid-cie-oidc-django/blob/main/spid_cie_oidc/authority/tests/test_02_trust_anchor_intermediary.py#L32).
