import datetime
import logging

from collections import OrderedDict
from typing import Union, Optional, List

from spid_cie_oidc.entity.policy import apply_policy

from .exceptions import (
    InvalidEntityConfiguration,
    InvalidRequiredTrustMark,
    MetadataDiscoveryException,
)

from .statements import (
    get_entity_configurations,
    EntityConfiguration,
)
from .utils import datetime_from_timestamp


logger = logging.getLogger(__name__)


class TrustChainBuilder:
    """
    A trust walker that fetches statements and evaluate the evaluables

    max_intermediaries means how many hops are allowed to the trust anchor
    max_authority_hints means how much authority_hints to follow on each hop

    required_trust_marks means all the trsut marks needed to start a metadata discovery
     at least one of the required trust marks is needed to start a metadata discovery
     if this param if absent the filter won't be considered.
    """

    def __init__(
        self,
        subject: str,
        trust_anchor: Union[str, EntityConfiguration],
        httpc_params: dict = {},
        max_authority_hints: int = 10,
        subject_configuration: EntityConfiguration = None,
        required_trust_marks: list = [],
        # TODO - prefetch cache?
        # pre_fetched_entity_configurations = {},
        # pre_fetched_statements = {},
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

        self.tree_of_trust = OrderedDict()
        self.trust_path = []  # list of valid subjects up to trust anchor

        self.max_authority_hints = max_authority_hints
        # dynamically valued
        self.max_path_len = 0
        self.final_metadata: dict = {}

        self.verified_trust_marks = []
        self.exp = 0

    def apply_metadata_policy(self) -> dict:
        """
        Starts the search for a trust path and, if found, applies the
        metadata policies to generate the final metadata.
        """
        logger.info(
            f"Starting trust path search for {self.subject} to "
            f"{self.trust_anchor_configuration.sub}"
        )


        start_path = [self.subject_configuration]

        valid_path = self._find_trust_path_recursive(start_path)

        if valid_path:
            logger.info(f"Found a valid trust path: {[e.sub for e in valid_path]}")
            self.trust_path = valid_path

            final_metadata = self.subject_configuration.payload.get("metadata", {})
            if not final_metadata:
                logger.error(f"Missing metadata in subject {self.subject}")
                return {}

            for i in range(len(self.trust_path) - 1, 0, -1):
                superior_ec = self.trust_path[i]
                subordinate_ec = self.trust_path[i-1]

                statement = superior_ec.verified_descendant_statements.get(subordinate_ec.sub, {})
                policy = statement.get("metadata_policy", {})

                for md_type, pol_value in policy.items():
                    if final_metadata.get(md_type):
                        final_metadata[md_type] = apply_policy(
                            final_metadata[md_type], pol_value
                        )

            self.final_metadata = final_metadata
            self.set_exp()
            return self.final_metadata
        else:
            logger.warning(
                f"Could not find a valid trust path for {self.subject} "
                f"to {self.trust_anchor_configuration.sub}"
            )
            self.trust_path = []
            return {}

    def _find_trust_path_recursive(self, current_path: list) -> Optional[list]:
        """
        Recursively searches for a valid trust path (Depth-First Search).

        Args:
            current_path: The list of EntityConfigurations in the current path.

        Returns:
            The list representing the complete path if found, otherwise None.
        """
        last_entity = current_path[-1]

        # Base case (SUCCESS): we have reached the trust anchor
        if last_entity.sub == self.trust_anchor_configuration.sub:
            return current_path

        # Base case (FAILURE): path has exceeded the maximum allowed length
        # The +1 is because max_path_len is the number of intermediaries
        if len(current_path) > self.max_path_len + 1:
            logger.warning(
                f"Path length ({len(current_path)}) exceeds max_path_len "
                f"({self.max_path_len}). Backtracking."
            )
            return None

        for superior_ec in last_entity.verified_by_superiors.values():

            # Loop prevention: do not visit an entity that is already in the path
            if superior_ec.sub in [e.sub for e in current_path]:
                logger.warning(f"Loop detected with entity {superior_ec.sub}. Skipping path.")
                continue

            new_path = current_path + [superior_ec]
            result = self._find_trust_path_recursive(new_path)

            # If the recursive call found a path, propagate the result upwards
            if result:
                return result

        # If the loop finishes, it means no superior led to a solution
        return None

    @property
    def exp_datetime(self) -> datetime.datetime:
        if self.exp:  # pragma: no cover
            return datetime_from_timestamp(self.exp)

    def set_exp(self) -> int:
        exps = [i.payload["exp"] for i in self.trust_path]
        if exps:
            self.exp = min(exps)

    def discovery(self) -> bool:
        """
        return a chain of verified statements
        from the lower up to the trust anchor
        """
        logger.info(f"Starting a Walk into Metadata Discovery for {self.subject}")
        self.tree_of_trust[0] = [self.subject_configuration]

        ecs_history = []
        while (len(self.tree_of_trust) - 2) < self.max_path_len:
            last_path_n = list(self.tree_of_trust.keys())[-1]
            last_ecs = self.tree_of_trust[last_path_n]

            sup_ecs = []
            for last_ec in last_ecs:
                # Metadata discovery loop prevention
                if last_ec.sub in ecs_history:
                    logger.warning(
                        f"Metadata discovery loop detection for {last_ec.sub}. "
                        f"Already present in {ecs_history}. "
                        "Discovery blocked for this path."
                    )
                    continue

                try:
                    superiors = last_ec.get_superiors(
                        max_authority_hints=self.max_authority_hints,
                        superiors_hints=[self.trust_anchor_configuration],
                    )
                    validated_by = last_ec.validate_by_superiors(
                        superiors_entity_configurations=superiors.values()
                    )
                    vbv = list(validated_by.values())
                    sup_ecs.extend(vbv)
                    ecs_history.append(last_ec)
                except MetadataDiscoveryException as e:
                    logger.exception(
                        f"Metadata discovery exception for {last_ec.sub}: {e}"
                    )

            if sup_ecs:
                self.tree_of_trust[last_path_n + 1] = sup_ecs
            else:
                break

        last_path = list(self.tree_of_trust.keys())[-1]
        if (
            self.tree_of_trust[0][0].is_valid
            and self.tree_of_trust[last_path][0].is_valid
        ):
            self.is_valid = True
            self.apply_metadata_policy()

        return self.is_valid

    def get_trust_anchor_configuration(self) -> None:
        if isinstance(self.trust_anchor, EntityConfiguration):
            self.trust_anchor_configuration = self.trust_anchor

        elif not self.trust_anchor_configuration and isinstance(self.trust_anchor, str):
            logger.info(f"Starting Metadata Discovery for {self.subject}")
            ta_jwt = get_entity_configurations(
                self.trust_anchor, httpc_params=self.httpc_params
            )[0]
            self.trust_anchor_configuration = EntityConfiguration(ta_jwt)

        try:
            self.trust_anchor_configuration.validate_by_itself()
        except Exception as e:  # pragma: no cover
            _msg = (
                f"Trust Anchor Entity Configuration failed for {self.trust_anchor}. "
                f"{e}"
            )
            logger.error(_msg)
            raise Exception(_msg)

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
            try:
                jwt = get_entity_configurations(
                    self.subject, httpc_params=self.httpc_params
                )
                self.subject_configuration = EntityConfiguration(
                    jwt[0], trust_anchor_entity_conf=self.trust_anchor_configuration
                )
                self.subject_configuration.validate_by_itself()
            except Exception as e:
                _msg = f"Entity Configuration for {self.subject} failed: {e}"
                logger.error(_msg)
                raise InvalidEntityConfiguration(_msg)

            # Trust Mark filter
            if self.required_trust_marks:
                sc = self.subject_configuration
                sc.filter_by_allowed_trust_marks = self.required_trust_marks

                # TODO: create a proxy function that gets tm issuers ec from
                # a previously populated cache
                # sc.trust_mark_issuers_entity_confs = [
                # trust_mark_issuers_entity_confs
                # ]
                if not sc.validate_by_allowed_trust_marks():
                    raise InvalidRequiredTrustMark(
                        "The required Trust Marks are not valid"
                    )
                else:
                    self.verified_trust_marks.extend(sc.verified_trust_marks)

    def serialize(self):
        res = []
        # we have only the leaf's and TA's EC, all the intermediate EC will be dropped
        ta_ec: str = ""
        for stat in self.trust_path:
            if not isinstance(self.trust_anchor, str):
                if (self.subject == stat.sub == stat.iss):
                    res.append(stat.jwt)
                elif (self.trust_anchor.sub == stat.sub == stat.iss):
                    ta_ec = stat.jwt

            if stat.verified_descendant_statements:
                res.extend(
                    [
                        i for i in stat.verified_descendant_statements_as_jwt.values()
                    ]
                )
        if ta_ec:
            res.append(ta_ec)
        return res

    def start(self):
        try:
            self.get_trust_anchor_configuration()
            self.get_subject_configuration()
            self.discovery()
        except Exception as e:
            self.is_valid = False
            logger.error(f"{e}")
            raise e