# OP's Revocation Endpoint
The OP's Revocation Endpoint provides a mechanism that allows an RP to invalidate its tokens.

In spid_cie_oidc.onboarding.schemas there are functions to generate the json schema of the Revocation Request to the OP's Revocation Endpoint from RP. 
RP Revocation  Endpoint responds in any case with HTTP status code 200.

With the same functions is possible to validate request.


# How to export the revocation request schema for SPID

````
./manage.py shell
from spid_cie_oidc.onboarding.schemas.revocation_request import RevocationRequest
print(RevocationRequest.schema_json(indent=2))
````

# How to validate a revocation request for SPID

````
./manage.py shell
````
Import a revocation request example
````
from spid_cie_oidc.onboarding.tests.revocation_request_settings import REVOCATION_REQUEST
````
Then to validate
````
from spid_cie_oidc.onboarding.schemas.revocation_request import RevocationRequest
RevocationRequest(**REVOCATION_REQUEST)
````
