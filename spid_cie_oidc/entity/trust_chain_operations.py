import logging

from django.utils import timezone
from typing import Union

from .exceptions import InvalidTrustchain, TrustchainMissingMetadata
from .models import FetchedEntityStatement, TrustChain
from .statements import EntityConfiguration, get_entity_configurations
from .settings import HTTPC_PARAMS
from .trust_chain import TrustChainBuilder
from .utils import datetime_from_timestamp

logger = logging.getLogger(__name__)


def trust_chain_builder(
    subject: str,
    trust_anchor: EntityConfiguration,
    httpc_params: dict = HTTPC_PARAMS,
    required_trust_marks: list = []
) -> Union[TrustChainBuilder, bool]:
    """
        Trust Chain builder
    """
    tc = TrustChainBuilder(
        subject,
        trust_anchor=trust_anchor,
        required_trust_marks=required_trust_marks,
        httpc_params=httpc_params
    )
    tc.start()

    if not tc.is_valid:
        logger.error(
            "The tree of trust cannot be validated for "
            f"{tc.subject}: {tc.tree_of_trust}"
        )
        return False
    else:
        return tc


def dumps_statements_from_trust_chain_to_db(trust_chain: TrustChainBuilder) -> list:

    entity_statements = []

    for stat in trust_chain.trust_path:

        data = dict(
            exp=datetime_from_timestamp(stat.payload["exp"]),
            iat=datetime_from_timestamp(stat.payload["iat"]),
            statement=stat.payload,
            jwt=stat.jwt,
        )

        fes = FetchedEntityStatement.objects.filter(sub=stat.sub, iss=stat.iss)

        if fes:
            fes.update(**data)
        else:
            fes = FetchedEntityStatement.objects.create(
                sub=stat.sub, iss=stat.iss, **data
            )

        entity_statements.append(fes)

        if stat.verified_descendant_statements:

            for desc_stat_sub in stat.verified_descendant_statements:
                payload = stat.verified_descendant_statements[desc_stat_sub]
                jwt = stat.verified_descendant_statements_as_jwt[desc_stat_sub]

                _data = dict(
                    exp=datetime_from_timestamp(payload["exp"]),
                    iat=datetime_from_timestamp(payload["iat"]),
                    statement=payload,
                    jwt=jwt,
                )

                desc_fes = FetchedEntityStatement.objects.filter(
                    sub=payload["sub"], iss=payload["iss"]
                )

                if desc_fes:
                    desc_fes.update(**_data)
                else:
                    desc_fes = FetchedEntityStatement.objects.create(
                        sub=payload["sub"], iss=payload["iss"], **_data
                    )

                entity_statements.append(desc_fes)

    return entity_statements


def get_or_create_trust_chain(
    subject: str,
    trust_anchor: str,
    httpc_params: dict = HTTPC_PARAMS,
    required_trust_marks: list = [],
    force: bool = False,
) -> Union[TrustChain, None]:
    """
    returns a TrustChain model object if any available
    if available it return it
    if not available it create a new one

    if available and expired it return the expired one
    if flag force is set to True -> renew the trust chain, update it and
    return the updated one

    """
    fetched_trust_anchor = FetchedEntityStatement.objects.filter(
        sub=trust_anchor, iss=trust_anchor
    )
    if not fetched_trust_anchor or fetched_trust_anchor.first().is_expired or force:

        jwts = get_entity_configurations([trust_anchor], httpc_params=httpc_params)
        ta_conf = EntityConfiguration(jwts[0], httpc_params=httpc_params)

        data = dict(
            exp=datetime_from_timestamp(ta_conf.payload["exp"]),
            iat=datetime_from_timestamp(ta_conf.payload["iat"]),
            statement=ta_conf.payload,
            jwt=ta_conf.jwt,
        )

        if not fetched_trust_anchor:
            # trust to the anchor should be absolute trusted!
            # ta_conf.validate_by_itself()
            fetched_trust_anchor = FetchedEntityStatement.objects.create(
                sub=ta_conf.sub, iss=ta_conf.iss, **data
            )
        else:
            fetched_trust_anchor.update(
                exp=datetime_from_timestamp(ta_conf.payload["exp"]),
                iat=datetime_from_timestamp(ta_conf.payload["iat"]),
                statement=ta_conf.payload,
                jwt=ta_conf.jwt,
            )
            fetched_trust_anchor = fetched_trust_anchor.first()

    else:
        fetched_trust_anchor = fetched_trust_anchor.first()
        ta_conf = fetched_trust_anchor.get_entity_configuration_as_obj()

    tc = TrustChain.objects.filter(sub=subject, trust_anchor__sub=trust_anchor).first()

    if tc and not tc.is_active:
        # if manualy disabled by staff
        return None
    elif force or not tc or tc.is_expired:
        trust_chain = trust_chain_builder(
            subject=subject,
            trust_anchor=ta_conf,
            required_trust_marks=required_trust_marks
        )
        if not trust_chain:
            raise InvalidTrustchain(
                f"Trust chain for subject {subject} and "
                f"trust_anchor {trust_anchor} is not found"
            )
        elif not trust_chain.is_valid:
            raise InvalidTrustchain(
                f"Trust chain for subject {subject} and "
                f"trust_anchor {trust_anchor} is not valid"
            )
        elif not trust_chain.final_metadata:
            raise TrustchainMissingMetadata(
                f"Trust chain for subject {subject} and "
                f"trust_anchor {trust_anchor} doesn't have any metadata"
            )
        dumps_statements_from_trust_chain_to_db(trust_chain)

        tc = TrustChain.objects.filter(
            sub=subject, trust_anchor__sub=trust_anchor
        )
        data = dict(
            exp=trust_chain.exp_datetime,
            processing_start = timezone.localtime(),
            chain=trust_chain.serialize(),
            jwks = trust_chain.subject_configuration.jwks,
            metadata=trust_chain.final_metadata,
            parties_involved=[i.sub for i in trust_chain.trust_path],
            status="valid",
            trust_marks=[
                {"id": i.id, "trust_mark": i.jwt}
                for i in trust_chain.verified_trust_marks
            ],
            is_active=True,
        )

        if tc:
            tc.update(**data)
            tc = tc.first()
        else:
            tc = TrustChain.objects.create(
                sub=subject,
                trust_anchor=fetched_trust_anchor,
                **data,
            )

    return tc
