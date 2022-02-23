# How to export the validation authen response schema for SPID

````
./manage.py shell
from spid_cie_oidc.onboarding.schemas.authn_response import AuthenticationResponse
print(AuthenticationResponse.schema_json(indent=2))
````

# How to validate an authn response for SPID

````
./manage.py shell
````
Import an authn request example
````
from spid_cie_oidc.onboarding.tests.authn_responses_settings import AUTHN_RESPONSE_SPID
````
Then to validate
````
from spid_cie_oidc.onboarding.schemas.authn_response import AuthenticationResponse
AuthenticationResponse(**AUTHN_RESPONSE_SPID)
````

# How to export the validation authen error response schema for SPID

````
./manage.py shell
from spid_cie_oidc.onboarding.schemas.authn_response import AuthenticationErrorResponse
print(AuthenticationErrorResponse.schema_json(indent=2))
````

# How to validate an authn error response for SPID

````
./manage.py shell
````
Import an authn request example
````
from spid_cie_oidc.onboarding.tests.authn_responses_settings import AUTHN_ERROR_RESPONSE_SPID
````
Then to validate
````
from spid_cie_oidc.onboarding.schemas.authn_response import AuthenticationErrorResponse
AuthenticationErrorResponse(**AUTHN_ERROR_RESPONSE_SPID)
````