import datetime
import logging

from collections import OrderedDict
from typing import Union

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
        filters the trust path from subject to trust anchor
        apply the metadata policies along the path and
        returns the final metadata
        """
        # find the path of trust
        if not self.trust_path:
            self.trust_path = [self.subject_configuration]
        elif self.trust_path[-1].sub == self.trust_anchor_configuration.sub:
            # ok trust path completed, I just have to return over all the parent calls
            return

        logger.info(
            f"Applying metadata policy for {self.subject} over "
            f"{self.trust_anchor_configuration.sub} starting from "
            f"{self.trust_path[-1]}"
        )
        last_path = self.tree_of_trust[len(self.trust_path) - 1]

        path_found = False
        for ec in last_path:
            for sup_ec in ec.verified_by_superiors.values():
                while len(self.trust_path) - 2 < self.max_path_len:
                    if sup_ec.sub == self.trust_anchor_configuration.sub:
                        self.trust_path.append(sup_ec)
                        path_found = True
                        break
                    if sup_ec.verified_by_superiors:
                        self.trust_path.append(sup_ec)
                        self.apply_metadata_policy()
                    else:
                        logger.info(
                            f"'Cul de sac' in {sup_ec.sub} for {self.subject} "
                            f"to {self.trust_anchor_configuration.sub}"
                        )
                        self.trust_path = [self.subject_configuration]
                        break

        # once I filtered a concrete and unique trust path I can apply the metadata policy
        if path_found:
            logger.info(f"Found a trust path: {self.trust_path}")
            self.final_metadata = self.subject_configuration.payload.get("metadata", {})
            if not self.final_metadata:
                logger.error(
                    f"Missing metadata in {self.subject_configuration.payload['metadata']}"
                )
                return

            for i in range(len(self.trust_path))[::-1]:
                self.trust_path[i - 1].sub
                _pol = (
                    self.trust_path[i]
                    .verified_descendant_statements.get("metadata_policy", {})
                )
                for md_type, md in _pol.items():
                    if not self.final_metadata.get(md_type):
                        continue
                    self.final_metadata[md_type] = apply_policy(
                        self.final_metadata[md_type], _pol[md_type]
                    )

        # set exp
        self.set_exp()
        return self.final_metadata

    @property
    def exp_datetime(self) -> datetime.datetime:
        if self.exp:# pragma: no cover
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
        except Exception as e: # pragma: no cover
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
        ta_ec:str = ""
        for stat in self.trust_path:
            if not isinstance(self.trust_anchor, str):
                if (self.subject == stat.sub == stat.iss):
                    res.append(stat.jwt)
                elif (self.trust_anchor.sub == stat.sub == stat.iss):
                    ta_ec = stat.jwt

            if stat.verified_descendant_statements:
                res.append(
                    # [dict(i) for i in stat.verified_descendant_statements.values()]
                    [i for i in stat.verified_descendant_statements_as_jwt.values()]
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
