# How to export the introspection response schema for SPID

````
./manage.py shell
from spid_cie_oidc.onboarding.schemas.introspection_response import IntrospectionResponse
print(IntrospectionResponse.schema_json(indent=2))
````

# How to validate an introspection response for SPID

````
./manage.py shell
````
Import an authn request example
````
from spid_cie_oidc.onboarding.tests.introspection_response_settings import INTROSPECTION_RESPONSE
````
Then to validate
````
from spid_cie_oidc.onboarding.schemas.introspection_response import IntrospectionResponse
IntrospectionResponse(**INTROSPECTION_RESPONSE)
````

# How to export the introspection error response schema for SPID

````
./manage.py shell
from spid_cie_oidc.onboarding.schemas.introspection_response import IntrospectionErrorResponseSpid
print(IntrospectionErrorResponseSpid.schema_json(indent=2))
````

# How to validate an introspection error response for SPID

````
./manage.py shell
````
Import an authn request example
````
from spid_cie_oidc.onboarding.tests.introspection_response_settings import INTROSPECTION_ERROR_RESPONSE
````
Then to validate
````
from spid_cie_oidc.onboarding.schemas.introspection_response import IntrospectionErrorResponseSpid
IntrospectionErrorResponseSpid(**INTROSPECTION_ERROR_RESPONSE)
````