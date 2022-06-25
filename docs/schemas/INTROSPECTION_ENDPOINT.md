# OP's Introspection Endpoint
Introspection Endpoint provides metadata for a given token that was presented to it by an RP.

In spid_cie_oidc.provider.schemas there are functions to generate the json schema of the Introspection Request to the OP's Introspection Endpoint from RP and the related OP's response to RP.

With the same functions is possible to validate request and response.


# How to export the introspection request schema for SPID

````
./manage.py shell
from spid_cie_oidc.provider.schemas.introspection_request import IntrospectionRequest
print(IntrospectionRequest.schema_json(indent=2))
````

# How to validate an introspection request for SPID

````
./manage.py shell
````
Import an introspection request example
````
from spid_cie_oidc.provider.tests.introspection_request_settings import INTROSPECTION_REQUEST
````
Then to validate
````
from spid_cie_oidc.provider.schemas.introspection_request import IntrospectionRequest
IntrospectionRequest(**INTROSPECTION_REQUEST)
````

# How to export the introspection response schema for SPID

````
./manage.py shell
from spid_cie_oidc.provider.schemas.introspection_response import IntrospectionResponse
print(IntrospectionResponse.schema_json(indent=2))
````

# How to validate an introspection response for SPID

````
./manage.py shell
````
Import an introspection response example
````
from spid_cie_oidc.provider.tests.introspection_response_settings import INTROSPECTION_RESPONSE
````
Then to validate
````
from spid_cie_oidc.provider.schemas.introspection_response import IntrospectionResponse
IntrospectionResponse(**INTROSPECTION_RESPONSE)
````

# How to export the introspection error response schema for SPID

````
./manage.py shell
from spid_cie_oidc.provider.schemas.introspection_response import IntrospectionErrorResponseSpid
print(IntrospectionErrorResponseSpid.schema_json(indent=2))
````

# How to validate an introspection error response for SPID

````
./manage.py shell
````
Import an introspection error response example
````
from spid_cie_oidc.provider.tests.introspection_response_settings import INTROSPECTION_ERROR_RESPONSE
````
Then to validate
````
from spid_cie_oidc.provider.schemas.introspection_response import IntrospectionErrorResponseSpid
IntrospectionErrorResponseSpid(**INTROSPECTION_ERROR_RESPONSE)
````