## Tutorial

We can create our entity though the Admin backend or via API.

### Create a Federation Authority via web

__setup__
1. add `spid_cie_oidc.entity` and `spid_cie_oidc.authority` in settings.INSTALLED_APPS
2. do migrations `./manage.py migrate`
3. create superuser `./manage.py createsuperuser`
4. log in the `/admin` interface

__configure the federation entity__
1. Click on _Federation Entity Configuration_ and create your entity see `federation_authority` example


### Create a Federation Descendant via web

__configure descendants entities__
1. Click on _Federation Entity Descendant_ and configure a descendant
2. Click on _Federation Entity Profile_ and create the desidered profiles and trust marks template
3. Click on _Federation Entity Descendant Assigned Profile_ and assing at least a profile to the new descendant


![profile](images/profiles.png)
A profile that may be assigned to a Relying Party.


![profile](images/assigned_profile.png)
An assigned profile to a Relying Party.


### Create a Federation Authority via API

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

### Create a Federation Descendant via API

see [unit tests](https://github.com/peppelinux/spid-cie-oidc-django/blob/main/spid_cie_oidc/authority/tests/test_02_trust_anchor_intermediary.py#L32).


### Create a CIE provider in a Federation Authority

Delete provider database:
````
cd examples/provider
rm db.sqlite3
````
do migrations ````./manage.py migrate````

in provider settingslocal.py configure cie profile:  ````OIDCFED_PROVIDER_PROFILE = "cie"````

In exemples/provider configure a federation entity configuration as OP:

````
./manage.py runserver 0.0.0.0:8002
````
In provider admin console:

![OP federation entity](images/op_federation_entity.png)

In examples/federation_authority configure OP cie as descendant:

````
./manage.py runserver
````

In federation admin console:

![OP as descendant](images/op_descendant.png)

In federation service build trust chain for OP:

````
examples/federation_authority/manage.py fetch_openid_providers --start -f
````