# How to export the token authn code request schema for SPID

````
./manage.py shell
from spid_cie_oidc.onboarding.validators.token_requests import TokenAuthnCodeRequest
print(TokenAuthnCodeRequest.schema_json(indent=2))
````

# How to validate a token authn code request for SPID

````
./manage.py shell
````
Import a token authn code request example
````
from spid_cie_oidc.onboarding.tests.token_request_settings import TOKEN_AUTHN_CODE_REQUEST
````
Then to validate
````
from spid_cie_oidc.onboarding.validators.token_requests import TokenAuthnCodeRequest
TokenAuthnCodeRequest(**TOKEN_AUTHN_CODE_REQUEST)
````

# How to export the token refresh request schema for SPID

````
./manage.py shell
from spid_cie_oidc.onboarding.validators.token_requests import TokenRefreshRequest
print(TokenRefreshRequest.schema_json(indent=2))
````

# How to validate a token refresh request for SPID

````
./manage.py shell
````
Import a token refresh request example
````
from spid_cie_oidc.onboarding.tests.token_request_settings import TOKEN_REFRESH_REQUEST
````
Then to validate
````
from spid_cie_oidc.onboarding.validators.token_requests import TokenRefreshRequest
TokenRefreshRequest(**TOKEN_REFRESH_REQUEST)
````

# How to export jwt schema for SPID

````
./manage.py shell
from spid_cie_oidc.onboarding.validators.token_requests import JwtClientAssertionStructureSpid
print(JwtClientAssertionStructureSpid.schema_json(indent=2))
````


# How to validate a jwt for SPID

````
./manage.py shell
````
Import a jwt example
````
from spid_cie_oidc.onboarding.tests.token_request_settings import JWT_CLIENT_ASSERTION_SPID
````
Then to validate
````
from spid_cie_oidc.onboarding.validators.token_requests import JwtClientAssertionStructureSpid
JwtClientAssertionStructureSpid(**JWT_CLIENT_ASSERTION_SPID)
````
