
from pydantic import BaseModel, HttpUrl,  constr, ValidationError, conlist
from typing import Literal, Optional

#vengono accettati anche altri campi oltre a quelli elencati

class ClaimsTypeEssential(BaseModel):
    essential: Optional[bool]

class ClaimsTypeStringValue(BaseModel):
    value: Optional[str]

class ClaimsTypeStringValues(BaseModel):
    values: Optional[conlist(str, max_items = 2)]

class UserInfo(BaseModel): 
    given_name: Optional[dict]
    family_name: Optional[dict]

class IdToken(UserInfo):
    pass

TYPES = {
    'essential': ClaimsTypeEssential,
    'value': ClaimsTypeStringValue,
    'values': ClaimsTypeStringValues,
}

CLAIMS = {
    'userinfo': UserInfo,
    'id_token': IdToken
}

class AuthenticationRequest(BaseModel):
    client_id: HttpUrl
    response_type: Literal['code']
    scope: Literal['openid']
    code_challenge: str 
    code_challenge_method: Literal['S256']
    nonce: constr(min_length = 32)
    prompt: Literal['consent', 'consent login', 'verify']
    redirect_uri: HttpUrl
    acr_values: constr(regex=r'https://www.spid.gov.it/SpidL[123](\shttps://www.spid.gov.it/SpidL[123])?(\shttps://www.spid.gov.it/SpidL[123])?$')
    claims : Optional[dict]
    state: constr(min_length = 32)
    
def validate_message(msg:dict) -> None:
    claims = msg['claims']
    for k,v in claims.items(): 
        claims_items = CLAIMS[k]
        claims_items(**v)
        for k_item, v_item in v.items():
            if v_item is not None:
                for k_type, v_type in TYPES.items():
                    validator = v_type
                    validator(**v_item)


