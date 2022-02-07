import logging
import requests

from collections import OrderedDict
from django.conf import settings

from . import settings as settings_local
from . exceptions import (
    TrustChainHttpError,
    EntityStatementUnknownKid
)
from . jwtse import (
    verify_jws,
    unpad_jwt_head,
    unpad_jwt_payload
)

HTTPC_PARAMS = getattr(settings, "HTTPC_PARAMS", settings_local.HTTPC_PARAMS)
MAX_DISCOVERY_REQUESTS = getattr(
    settings, 'MAX_DISCOVERY_REQUESTS', settings_local.MAX_DISCOVERY_REQUESTS
)
logger = logging.getLogger(__name__)


class TrustChain:
    """

    """
    def __init__(
        self, subject:str, trust_anchor:str, httpc_params:dict = {},
        max_legth:int = 12, **kwargs
    ) -> None:
        
        self.subject = subject
        self.httpc_params = httpc_params
        self.trust_anchor = trust_anchor
        self.is_valid = False
        self.statements_collection = OrderedDict()
        self.endpoints_https_contents = OrderedDict()

    def get_entity_configuration(self, subject):
        _url = f"{subject}{settings_local.FEDERATION_WELLKNOWN_URL}"
        logger.info(f"Starting Metadata Discovery for {_url}")
        
        req = requests.get(_url, **self.httpc_params)
        if req.status_code != 200:
            self.is_valid = False
            raise TrustChainHttpError(
                f"{_url} returns http status code: {req.status_code}"
            )

        content = req.content.decode()
        self.endpoints_https_contents[_url] = (req.status_code, content)

        jwt_head = unpad_jwt_head(content)
        jwt_payload = unpad_jwt_payload(content)

        # TODO: pydantic entity configuration validation here

        _jwks = jwt_payload.get('jwks', [{}])
        kids = [i['kid'] for i in _jwks]
        if jwt_head.get('kid') not in kids:
            raise EntityStatementUnknownKid(
                f"{jwt_head.get('kid')} not found in {_jwks}"
            )

        # verify signature
        verify_jws(content, _jwks[kids.index(jwt_head['kid'])])
        
        self.statements_collection[_url] = jwt_payload
        self.is_valid = True

    def discover_authority_loop(self):
        breakpoint()
        pass
        
    def load(self):
        try:
            self.get_entity_configuration(self.subject)
            self.discover_authority_loop()
        except Exception as e:
            self.is_valid = False
            logger.error(f"{e}")
            raise e 
        

def trust_chain_builder(subject:str) -> TrustChain:
    """
        Minimal Provider Discovery endpoint request processing
    """
    tc = TrustChain(
        subject,
        settings.FEDERATION_TRUST_ANCHOR,
        httpc_params = HTTPC_PARAMS,
        max_length = MAX_DISCOVERY_REQUESTS
    )
    tc.load()

    if not tc.is_valid:
        last_url = tuple(tc.endpoints_https_contents.keys())[-1]
        logger.error(
            f"Got {tc.endpoints_https_contents[last_url][0]} for {last_url}"
        )


class OidcFederationTrustManager(object):
    """
        https://openid.net/specs/openid-connect-federation-1_0.html#rfc.section.3.2
    """

    def trust_cached(self, subject):
        """
            Checks if we already have a valid trust chains for this sub

            saves the trust chain and returns it
        """
        pass



    def get_jwks_from_jwks_uri(self,
                               jwks_uri:str,
                               verify:bool=True)->tuple:
        """
            builds jwks objects, importable in a Key Jar
        """
        jwks_dict = requests.get(jwks_uri, verify=verify).json()
        return jwks_dict, [key_from_jwk_dict(i) for i in jwks_dict["keys"]]
