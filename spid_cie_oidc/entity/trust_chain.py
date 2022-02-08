import logging
import requests

from collections import OrderedDict
from django.conf import settings

from . import settings as settings_local
from . exceptions import HttpError
from . statements import get_statement, EntityConfiguration


HTTPC_PARAMS = getattr(settings, "HTTPC_PARAMS", settings_local.HTTPC_PARAMS)
FEDERATION_WELLKNOWN_URL = getattr(
    settings, 'FEDERATION_WELLKNOWN_URL', settings_local.FEDERATION_WELLKNOWN_URL
)
MAXIMUM_AUTHORITY_HINTS = getattr(
    settings, 'MAXIMUM_AUTHORITY_HINTS', settings_local.MAXIMUM_AUTHORITY_HINTS
)
MAX_DISCOVERY_REQUESTS = getattr(
    settings, 'MAX_DISCOVERY_REQUESTS', settings_local.MAX_DISCOVERY_REQUESTS
)
logger = logging.getLogger(__name__)


class TrustChainBuilder:
    """
        A trust walker that fetches statements and evaluate the evaluables
    """
    def __init__(
        self, subject:str, trust_anchor:str, httpc_params:dict = {},
        max_path_length:int = None, **kwargs
    ) -> None:
        
        self.subject = subject
        self.httpc_params = httpc_params
        self.trust_anchor = trust_anchor
        self.max_path_length = max_path_length or MAX_DISCOVERY_REQUESTS
        self.is_valid = False
        self.statements_collection = OrderedDict()
        self.entity_configuration:EntityConfiguration = None

    def apply_metadata_policy(self) -> dict:
        """
            returns the final metadata
        """
        # TODO
        return {}

    def metadata_discovery(self, jwt):
        logger.info(f"Starting Metadata Discovery for {self.subject}")
        ec = self.entity_configuration = EntityConfiguration(jwt)

        # here we decide the discovery policy
        # how many hints we'll follow
        # if we want to give to them a priority
        if not ec.get_superiors():
            # TODO: check is this subject matches to a trust anchor
            pass

        

        
    def get_entity_configuration(self):
        url = f"{self.subject}{FEDERATION_WELLKNOWN_URL}"
        logger.info(f"Starting Entity Configuration Request for {url}")
        jwt = get_statement(url)
        return jwt

    def start(self):
        try:
            jwt = self.get_entity_configuration(
                self.subject, httpc_params = self.httpc_params
            )
            self.metadata_discovery(jwt)
        except Exception as e:
            self.is_valid = False
            logger.error(f"{e}")
            raise e 


def trust_chain_builder(subject:str, httpc_params:dict = {}) -> TrustChain:
    """
        Minimal Provider Discovery endpoint request processing
    """
    tc = TrustChainBuilder(
        subject,
        settings.FEDERATION_TRUST_ANCHOR,
        httpc_params = HTTPC_PARAMS,
        max_length = MAX_DISCOVERY_REQUESTS
    )
    tc.start()

    if not tc.is_valid:
        last_url = tuple(tc.endpoints_https_contents.keys())[-1]
        logger.error(
            f"Got {tc.endpoints_https_contents[last_url][0]} for {last_url}"
        )


class OidcFederationTrustManager:
    """
        https://openid.net/specs/openid-connect-federation-1_0.html#rfc.section.3.2
    """

    def trust_cached(self, subject):
        """
            Checks if we already have a valid trust chains for this sub

            saves the trust chain and returns it
        """
        pass
