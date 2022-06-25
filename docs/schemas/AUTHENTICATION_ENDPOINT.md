# OP’s Authorization Endpoint

In spid_cie_oidc.provider.schemas there are functions to generate the json schema of the Authentication Request to the OP's Authorization Endpoint from RP and the related OP's response to RP.

With the same functions is possible to validate request and response.


# How to export the authn request schema for SPID

````
./manage.py shell
from spid_cie_oidc.provider.schemas.authn_requests import AuthenticationRequestSpid
print(AuthenticationRequestSpid.schema_json(indent=2))
````

# How to validate an authn request for SPID

````
./manage.py shell
````
Import an authn request example
````
from spid_cie_oidc.provider.tests.authn_request_settings import AUTHN_REQUEST_SPID
````
Then to validate
````
from spid_cie_oidc.provider.schemas.authn_requests import AuthenticationRequestSpid
AuthenticationRequestSpid(**AUTHN_REQUEST_SPID)
````

# How to export the authn successful response schema for SPID

````
./manage.py shell
from spid_cie_oidc.provider.schemas.authn_response import AuthenticationResponse
print(AuthenticationResponse.schema_json(indent=2))
````

# How to validate an authn successful response for SPID

````
./manage.py shell
````
Import an authn successful response example
````
from spid_cie_oidc.provider.tests.authn_responses_settings import AUTHN_RESPONSE_SPID
````
Then to validate
````
from spid_cie_oidc.provider.schemas.authn_response import AuthenticationResponse
AuthenticationResponse(**AUTHN_RESPONSE_SPID)
````

# How to export the authn error response schema for SPID

````
./manage.py shell
from spid_cie_oidc.provider.schemas.authn_response import AuthenticationErrorResponse
print(AuthenticationErrorResponse.schema_json(indent=2))
````

# How to validate an authn error response for SPID

````
./manage.py shell
````
Import an authn error response example
````
from spid_cie_oidc.provider.tests.authn_responses_settings import AUTHN_ERROR_RESPONSE_SPID
````
Then to validate
````
from spid_cie_oidc.provider.schemas.authn_response import AuthenticationErrorResponse
AuthenticationErrorResponse(**AUTHN_ERROR_RESPONSE_SPID)
````

