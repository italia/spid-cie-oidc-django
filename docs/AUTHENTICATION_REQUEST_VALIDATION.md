# How to export the validotion request schema

````
./manage.py shell
from spid_cie_oidc.onboarding.authn_requests.schemas import AuthenticationRequest
print(AuthenticationRequest.schema_json(indent=2))
````