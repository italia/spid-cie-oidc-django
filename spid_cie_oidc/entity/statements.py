from . exceptions import UnknownKid
from . jwtse import (
    verify_jws,
    unpad_jwt_head,
    unpad_jwt_payload
)


def jwks_from_jwks_uri(jwks_uri:str, httpc_params:dict = {}) -> dict:
    try:
        jwks_dict = requests.get(jwks_uri, **httpc_params).json()
        return jwks_dict
    except Exception as e:
        logger.error(f"Connecting to {jwks_uri}: {e}")
        return [{}]


def get_jwks(jwt_payload:dict, httpc_params:dict = {}):
    return (
        self.payload.get('jwks') or
        jwks_from_jwks_uri(jwks_uri, httpc_params)
    )


def get_statement(url:dict, httpc_params:dict = {}) -> EntityConfiguration:
    """
        Fetches an entity statement/configuration
    """
    req = requests.get(_url, **httpc_params)
    if req.status_code != 200:
        raise HttpError(
            f"{_url} returns http status code: {req.status_code}"
        )
    return req.content.decode()


class EntityConfiguration:
    """
        The self issued/signed statement of a federation entity
    """

    def __init__(self, jwt:str, httpc_params:dict = {}):
        self.jwt = jwt
        self.header = unpad_jwt_head(jwt)
        self.payload = unpad_jwt_payload(jwt)
        self.is_valid = False
        self.jwks = get_jwks(self.payload, httpc_params)
        self.kids = [i.get('kid') for i in _jwks]
        self.httpc_params = httpc_params

        # a dict with sup_sub : superior entity configuration
        self.verified_superiors = {}
        # as previous but with superiors with invalid entity configurations
        self.failed_superiors = {}

        # a dict with sup_sub : entity statement issued for self
        self.verified_by_superiors = {}
        self.failed_by_superiors = {}

    def validate_by_itself(self) -> bool:
        """
            validates the entity configuration by it self
        """
        # TODO: pydantic entity configuration validation here
        if jwt_head.get('kid') not in self.kids:
            raise UnknownKid(
                f"{self.header.get('kid')} not found in {self.jwks}"
            )
        # verify signature
        verify_jws(self.jwt, self.jwks[self.kids.index(self.header['kid'])])
        self.is_valid = True
        return True

    def get_superiors(self, authority_hints:list = []) -> list[EntityConfiguration]:
        """
            get superiors entity configurations
        """
        # apply limits if defined
        authority_hints = authority_hints or self.payload['authority_hints']

        for sup_url in authority_hints:
            jwt = get_statement(sup_url, self.httpc_params)
            ec = self.__class__(jwt, httpc_params=self.httpc_params)

            if ec.validate_by_itself():
                target = self.verified_superiors
            else:
                target = self.failed_superiors

            target[ec.payload['sub']] = payload
        return self.verified_superiors
    
    def validate_descendant_statement(self, jwt:str) -> bool:
        """
            jwt is a descendant entity statement issued by self
        """
        # TODO: pydantic entity configuration validation here
        header = unpad_jwt_head(jwt)
        payload = unpad_jwt_payload(jwt)
        if jwt_head.get('kid') not in self.kids:
            raise UnknownKid(
                f"{self.header.get('kid')} not found in {self.jwks}"
            )
        # verify signature
        verify_jws(jwt, self.jwks[self.kids.index(header['kid'])])
        return True
    
    def validate_by_superior_statement(
            self, jwt:str, ec:EntityConfiguration) -> bool:
        """
            statement jwt issued by a superior
            validated with the jwks contained in the Entity Configuration
            of the superior

            then the validated statement have to carry
            the pub jwks to validate self
        """
        is_valid = None
        superior_sub = ec.payload.get('sub')
        try:
            ec.validate_by_itself()
            payload = unpad_jwt_payload(jwt)
            _jwks = get_jwks(self.payload, self.httpc_params)
            _kids = [i.get('kid') for i in _jwks]
            verify_jws(self.jwt, _jwks[_kids.index(header['kid'])])
            is_valid = True
        except Exception:
            is_valid = False
            
        if is_valid:
            target = self.verified_superiors
        else:
            target = self.failed_superiors

        target[superior_sub] = payload
        return is_valid
        
    def validate_by_superiors(
            self,
            superiors_entity_configurations:list[EntityConfiguration],
            max_superiors:int = 12
        ):
        """
            validates the entity configuration with the entity statements
            issued by its superiors
        """
        if len(superiors_entity_configurations) > max_superiors:
            logger.warning(
                f"Found {len(superiors_entity_configurations)} but "
                f"authority maximum hints is set to {max_superiors}. "
                "the following authorities will be ignored: "
                f"{', '.join(superiors_entity_configurations[max_superiors:])}"
            )

        # TODO: asyncio loop
        for ec in superiors_entity_configurations[:max_superiors]:
            _invalid_ec_msg = (
                f"{ec.payload['sub']} is not a valid Entity Configuration. "
                "Skipped by EntityConfiguration.validate_by_superiors. "
            )
            if not ec.is_valid:
                logger.warning(_invalid_ec_msg)
                continue

            try:
                # get superior fetch url
                fetch_api_url = ec.payload['metadata']['federation_entity']['federation_api_endpoint']
            except KeyError:
                logger.warning(
                    _invalid_ec_msg
                    "Missing federation_api_endpoint in federation_entity metadata"
                )
                self.invalid_superiors[ec.payload['sub']] = validate_by_superior_statement(jwt, ec)
                continue

            else:
                jwt = get_statement(fetch_api_url, self.httpc_params)
                res[ec.payload['sub']] = validate_by_superior_statement(jwt, ec)
                
                

    def __str__(self) -> str:
        return f"{self.payload['sub']} valid {self.is_valid}"
