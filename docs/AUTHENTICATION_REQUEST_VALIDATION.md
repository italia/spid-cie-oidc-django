# How to export the validation request schema for SPID

````
./manage.py shell
from spid_cie_oidc.onboarding.validators.authn_requests import AuthenticationRequestSpid
print(AuthenticationRequestSpid.schema_json(indent=2))
````

# How to validate an authn request for SPID

````
./manage.py shell
````
Import an authn request example
````
from spid_cie_oidc.onboarding.tests.authn_request_settings import AUTHN_REQUEST_SPID
````
Then to validate
````
from spid_cie_oidc.onboarding.validators.authn_requests import AuthenticationRequestSpid
AuthenticationRequestSpid(**AUTHN_REQUEST_SPID)
````

