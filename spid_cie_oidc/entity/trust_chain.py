import logging

from collections import OrderedDict
from django.conf import settings
from typing import Union

from . import settings as settings_local
from . exceptions import HttpError
from . statements import (
    get_entity_configuration,
    get_statement,
    EntityConfiguration
)


HTTPC_PARAMS = getattr(settings, "HTTPC_PARAMS", settings_local.HTTPC_PARAMS)
OIDCFED_MAXIMUM_AUTHORITY_HINTS = getattr(
    settings, 'OIDCFED_MAXIMUM_AUTHORITY_HINTS', settings_local.OIDCFED_MAXIMUM_AUTHORITY_HINTS
)
OIDCFED_MAX_PATH_LEN = getattr(
    settings, 'OIDCFED_MAX_PATH_LEN', settings_local.OIDCFED_MAX_PATH_LEN
)
logger = logging.getLogger(__name__)


class TrustChainBuilder:
    """
        A trust walker that fetches statements and evaluate the evaluables

        max_intermediaries means how many hops are allowed to the trust anchor
        max_authority_hints means how much authority_hints to follow on each hop
    """
    def __init__(
        self, subject:str, trust_anchor:str, httpc_params:dict = {},
        max_intermediaries:int = 1, max_authority_hints:int = 10,
        **kwargs
    ) -> None:
        
        self.subject = subject
        self.httpc_params = httpc_params
        self.trust_anchor = trust_anchor
        self.is_valid = False
        self.statements_collection = OrderedDict()
        self.entity_configuration:Union[None, EntityConfiguration] = None
        self.tree_of_trust = OrderedDict()
        self.max_intermediaries = max_intermediaries
        
    def apply_metadata_policy(self) -> dict:
        """
            returns the final metadata
        """
        # TODO
        return {}

    def discover_trusted_superiors(self, ecs:list):
        for ec in ecs:
            ec.get_superiors()
            if not ec.verified_superiors:
                # TODO
                pass

        return ec

    def metadata_discovery(self, jwt) -> dict:
        """
            return a chain of verified statements
            from the lower up to the trust anchor
        """
        logger.info(f"Starting Metadata Discovery for {self.subject}")
        self.entity_configuration = EntityConfiguration(jwt)
        try:
            self.entity_configuration.validate_by_itself()
        except Exceptions as e:
            logger.error(
                f"Metadata Discovery Entity Configuration validation error: {e}"
            )
            return {}

        self.tree_of_trust[0] = [self.entity_configuration]
        # max_intermediaries - 2 means that root entity and trust anchor
        # are not considered as intermediaries
        while self.tree_of_trust < self.max_intermediaries - 2:
            # here we decide the discovery policy
            # how many hints we'll follow
            # if we want to give to them a priority
            
            # if not :
                # TODO: check is this subject matches to a trustable anchor
                # pass
                # break

            # for su
            pass

    def start(self):
        try:
            jwt = get_entity_configuration(
                self.subject, httpc_params = self.httpc_params
            )
            self.metadata_discovery(jwt)
        except Exception as e:
            self.is_valid = False
            logger.error(f"{e}")
            raise e 


def trust_chain_builder(subject:str, httpc_params:dict = {}) -> TrustChainBuilder:
    """
        Minimal Provider Discovery endpoint request processing
    """
    tc = TrustChainBuilder(
        subject,
        settings.OIDCFED_FEDERATION_TRUST_ANCHORS,
        httpc_params = HTTPC_PARAMS,
        max_length = OIDCFED_MAX_PATH_LEN
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
