# OP's Token Endpoint

The Token Endpoint issues Access Tokens, ID Tokens, and Refresh Tokens; there are two distinct scenarios in which the RP calls the Token Endpoint:

- At the end of the authentication flow, the RP calls the Token Endpoint by sending the authorization code received from the OP in the previous step to obtain an ID Token and an Access Token and possibly a Refresh Token 
- In the case the RP requests a Refresh Token, later it can use it at the Token Endpoint to obtain a new Access Token.

After receiving and validating a Token Request from the RP, the OP’s Token Endpoint returns a successful response, if the Token Request (both ID Token and Refresh Token) is invalid or unauthorized, the OP constructs the error response.

In spid_cie_oidc.provider.schemas there are functions to generate the json schema of the Token Request to the OP's Token Endpoint from RP and the related OP's response to RP.

With the same functions is possible to validate request and response.


# How to export the token authn code request schema for SPID

````
./manage.py shell
from spid_cie_oidc.provider.schemas.token_requests import TokenAuthnCodeRequest
print(TokenAuthnCodeRequest.schema_json(indent=2))
````

# How to validate a token authn code request for SPID

````
./manage.py shell
````
Import a token authn code request example
````
from spid_cie_oidc.provider.tests.token_request_settings import TOKEN_AUTHN_CODE_REQUEST
````
Then to validate
````
from spid_cie_oidc.provider.schemas.token_requests import TokenAuthnCodeRequest
TokenAuthnCodeRequest(**TOKEN_AUTHN_CODE_REQUEST)
````

# How to export the token refresh request schema for SPID

````
./manage.py shell
from spid_cie_oidc.provider.schemas.token_requests import TokenRefreshRequest
print(TokenRefreshRequest.schema_json(indent=2))
````

# How to validate a token refresh request for SPID

````
./manage.py shell
````
Import a token refresh request example
````
from spid_cie_oidc.provider.tests.token_request_settings import TOKEN_REFRESH_REQUEST
````
Then to validate
````
from spid_cie_oidc.provider.schemas.token_requests import TokenRefreshRequest
TokenRefreshRequest(**TOKEN_REFRESH_REQUEST)
````

# How to export the token authn code response schema for SPID

````
./manage.py shell
from spid_cie_oidc.provider.schemas.token_response import TokenResponse
print(TokenResponse.schema_json(indent=2))
````

# How to validate a token authn code response for SPID

````
./manage.py shell
````
Import a token authn code response example
````
from spid_cie_oidc.provider.tests.token_response_settings import TOKEN_RESPONSE
````
Then to validate
````
from spid_cie_oidc.provider.schemas.token_response import TokenResponse
TokenResponse(**TOKEN_RESPONSE)
````

# How to export the token refresh response schema for SPID

````
./manage.py shell
from spid_cie_oidc.provider.schemas.token_response import TokenRefreshResponse
print(TokenRefreshResponse.schema_json(indent=2))
````

# How to validate a token refresh response for SPID

````
./manage.py shell
````
Import a token refresh response example
````
from spid_cie_oidc.provider.tests.token_response_settings import TOKEN_REFRESH_RESPONSE
````
Then to validate
````
from spid_cie_oidc.provider.schemas.token_response import TokenRefreshResponse
TokenRefreshResponse(**TOKEN_REFRESH_RESPONSE)
````

# How to export the token error response schema for SPID

````
./manage.py shell
from spid_cie_oidc.provider.schemas.token_response import TokenErrorResponse
print(TokenErrorResponse.schema_json(indent=2))
````

# How to validate a token error response for SPID

````
./manage.py shell
````
Import a token error response example
````
from spid_cie_oidc.provider.tests.token_response_settings import TOKEN_ERROR_RESPONSE
````
Then to validate
````
from spid_cie_oidc.provider.schemas.token_response import TokenErrorResponse
TokenErrorResponse(**TOKEN_ERROR_RESPONSE)
````


# How to export jwt schema for SPID

````
./manage.py shell
from spid_cie_oidc.provider.schemas.jwt import JwtStructure
print(JwtStructure.schema_json(indent=2))
````


# How to validate a jwt for SPID

````
./manage.py shell
````
Import a jwt example
````
from spid_cie_oidc.provider.tests.token_request_settings import JWT_CLIENT_ASSERTION
````
Then to validate
````
from spid_cie_oidc.provider.schemas.jwt import JwtStructure
JwtStructure(**JWT_CLIENT_ASSERTION)
````
