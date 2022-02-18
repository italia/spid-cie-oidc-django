import logging

from collections import OrderedDict
from django.conf import settings
from typing import Union

from . import settings as settings_local
from .statements import (
    get_entity_configurations,
    EntityConfiguration,
)


HTTPC_PARAMS = getattr(settings, "HTTPC_PARAMS", settings_local.HTTPC_PARAMS)
OIDCFED_MAXIMUM_AUTHORITY_HINTS = getattr(
    settings,
    "OIDCFED_MAXIMUM_AUTHORITY_HINTS",
    settings_local.OIDCFED_MAXIMUM_AUTHORITY_HINTS,
)
logger = logging.getLogger(__name__)


class TrustChainBuilder:
    """
    A trust walker that fetches statements and evaluate the evaluables

    max_intermediaries means how many hops are allowed to the trust anchor
    max_authority_hints means how much authority_hints to follow on each hop
    """

    def __init__(
        self,
        subject: str,
        trust_anchor: Union[str, EntityConfiguration],
        httpc_params: dict = {},
        max_authority_hints: int = 10,
        subject_configuration: EntityConfiguration = None,
        required_trust_marks: list = [],

        # TODO - prefetch cache
        pre_fetched_entity_configurations = {},
        pre_fetched_statements = {},
        #
         
        **kwargs,
    ) -> None:

        self.subject = subject
        self.subject_configuration = subject_configuration
        self.httpc_params = httpc_params

        self.trust_anchor = trust_anchor
        self.trust_anchor_configuration = None
        
        self.required_trust_marks = required_trust_marks
        self.is_valid = False

        self.statements_collection = OrderedDict()
        self.tree_of_trust = OrderedDict()

        self.max_authority_hints = max_authority_hints

        # dynamically valued
        self.max_path_len = 0

    def apply_metadata_policy(self) -> dict:
        """
        returns the final metadata
        """
        # TODO
        return {}

    def discover_trusted_superiors(self, ecs: list):
        for ec in ecs:
            ec.get_superiors()
            if not ec.verified_superiors:
                # TODO
                pass

        return ec

    def validate_last_path_to_trust_anchor(self, ec: EntityConfiguration):
        logger.info(f"Validating {self.subject} with {self.trust_anchor}")

        # TODO: specialize exception
        # if not ec.payload.get("authority_hints"):
            
            # raise Exception(f"{ec.sub} doesn't have any authority hints!")
        # elif self.trust_anchor.sub not in ec["authority_hints"]:
            # raise Exception(
                # f"{self.subject} doesn't have {self.trust_anchor.sub} "
                # "in its authority hints "
                # f"but max_path_len is equal to {self.max_path_len}."
            # )
        if self.trust_anchor_configuration.sub not in ec.verified_by_superiors:
            vbs = ec.validate_by_superiors(
                superiors_entity_configurations=[self.trust_anchor]
            )
        else:
            vbs = ec.verified_by_superiors
            
        if not vbs:
            logger.warning(f"Trust chain failed for {self.subject}")
        else:
            self.is_valid = True
        
        # TODO
        # TODO: everything is ok right now ... apply metadata policy!

    def discovery(self) -> dict:
        """
        return a chain of verified statements
        from the lower up to the trust anchor
        """
        logger.info(f"Starting a Walk into Metadata Discovery for {self.subject}")
        self.tree_of_trust[0] = [self.subject_configuration]
        while (len(self.tree_of_trust) - 1) < self.max_path_len:
            last_path_n = list(self.tree_of_trust.keys())[-1]
            last_ecs = self.tree_of_trust[last_path_n]

            # check if trust_anchor is already available
            # TODO : here
            
            sup_ecs = []
            for last_ec in last_ecs:
                try:
                    superiors = last_ec.get_superiors(
                        max_authority_hints = self.max_authority_hints,
                        superiors_hints = [self.trust_anchor_configuration]
                    )
                    validated_by = last_ec.validate_by_superiors(
                        superiors_entity_configurations=superiors.values()
                    )
                    sup_ecs.extend(list(validated_by.values()))
                except Exception as e:
                    logger.exception(
                        f"Metadata discovery exception for {last_ec.sub}: {e}"
                    )

            self.tree_of_trust[last_path_n + 1] = sup_ecs

        # so we have all the intermediaries right now
        self.validate_last_path_to_trust_anchor(self.subject_configuration)

    def get_trust_anchor_configuration(self) -> None:

        if isinstance(self.trust_anchor, EntityConfiguration):
            self.trust_anchor_configuration = self.trust_anchor

        elif not self.trust_anchor_configuration and isinstance(self.trust_anchor, str):
            logger.info(f"Starting Metadata Discovery for {self.subject}")
            ta_jwt = get_entity_configurations(
                self.trust_anchor, httpc_params=self.httpc_params
            )
            self.trust_anchor_configuration = EntityConfiguration(ta_jwt)
            self.trust_anchor_configuration.validate_by_itself()

        # 
        if self.trust_anchor_configuration.payload.get("constraints", {}).get(
            "max_path_length"
        ):

            self.max_path_len = int(
                self.trust_anchor_configuration.payload["constraints"][
                    "max_path_length"
                ]
            )

    def get_subject_configuration(self) -> None:
        if not self.subject_configuration:
            jwt = get_entity_configurations(
                self.subject, httpc_params=self.httpc_params
            )
            self.subject_configuration = EntityConfiguration(jwt[0])
            self.subject_configuration.validate_by_itself()

            # TODO
            # TODO: self.subject_configuration.get_valid_trust_marks()
            # valid trust marks to be compared to self.required_trust_marks

    def start(self):
        try:
            self.get_trust_anchor_configuration()
            self.get_subject_configuration()
            self.discovery()
        except Exception as e:
            self.is_valid = False
            logger.error(f"{e}")
            raise e


def trust_chain_builder(
    subject: str,
    trust_anchor: EntityConfiguration,
    httpc_params: dict = {},
    required_trust_marks: list = [],
) -> TrustChainBuilder:
    """
    Minimal Provider Discovery endpoint request processing
    """
    tc = TrustChainBuilder(
        subject,
        trust_anchor=trust_anchor,
        required_trust_marks=required_trust_marks,
        httpc_params=HTTPC_PARAMS,
    )
    tc.start()

    if not tc.is_valid:
        last_url = tuple(tc.endpoints_https_contents.keys())[-1]
        logger.error(
            f"Got {tc.endpoints_https_contents[last_url][0]} for {last_url}"
        )
        return False
    else:
        return True

class OidcFederationTrustManager:
    """
    https://openid.net/specs/openid-connect-federation-1_0.html#rfc.section.3.2
    """

    def trust_cached(self, subject):
        """
        Checks if we already have a valid trust chains for this sub

        saves the trust chain and returns it
        """
