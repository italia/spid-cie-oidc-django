# How to export the token authn code response schema for SPID

````
./manage.py shell
from spid_cie_oidc.onboarding.schemas.token_response import TokenResponse
print(TokenResponse.schema_json(indent=2))
````

# How to validate a token authn code response for SPID

````
./manage.py shell
````
Import an authn request example
````
from spid_cie_oidc.onboarding.tests.token_response_settings import TOKEN_RESPONSE
````
Then to validate
````
from spid_cie_oidc.onboarding.schemas.token_response import TokenResponse
TokenResponse(**TOKEN_RESPONSE)
````

# How to export the token refresh response schema for SPID

````
./manage.py shell
from spid_cie_oidc.onboarding.schemas.token_response import TokenRefreshResponse
print(TokenRefreshResponse.schema_json(indent=2))
````

# How to validate a token refresh response for SPID

````
./manage.py shell
````
Import an authn request example
````
from spid_cie_oidc.onboarding.tests.token_response_settings import TOKEN_REFRESH_RESPONSE
````
Then to validate
````
from spid_cie_oidc.onboarding.schemas.token_response import TokenRefreshResponse
TokenRefreshResponse(**TOKEN_REFRESH_RESPONSE)
````

# How to export the token error response schema for SPID

````
./manage.py shell
from spid_cie_oidc.onboarding.schemas.token_response import TokenErrorResponse
print(TokenErrorResponse.schema_json(indent=2))
````

# How to validate a token error response for SPID

````
./manage.py shell
````
Import an authn request example
````
from spid_cie_oidc.onboarding.tests.token_response_settings import TOKEN_ERROR_RESPONSE
````
Then to validate
````
from spid_cie_oidc.onboarding.schemas.token_response import TokenErrorResponse
TokenErrorResponse(**TOKEN_ERROR_RESPONSE)
````