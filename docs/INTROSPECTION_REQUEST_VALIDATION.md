# How to export the introspection request schema for SPID

````
./manage.py shell
from spid_cie_oidc.onboarding.validators.introspection_request import IntrospectionRequest
print(IntrospectionRequest.schema_json(indent=2))
````

# How to validate an introspection request for SPID

````
./manage.py shell
````
Import an authn request example
````
from spid_cie_oidc.onboarding.tests.introspection_request_settings import INTROSPECTION_REQUEST
````
Then to validate
````
from spid_cie_oidc.onboarding.validators.introspection_request import IntrospectionRequest
IntrospectionRequest(**INTROSPECTION_REQUEST)
````