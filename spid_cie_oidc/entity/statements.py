from copy import deepcopy
from .exceptions import (
    UnknownKid,
    MissingJwksClaim,
    MissingTrustMark,
    TrustAnchorNeeded,
)
from .http_client import http_get
from .jwtse import verify_jws, unpad_jwt_head, unpad_jwt_payload

import asyncio
import json
import logging
import requests


try:
    from django.conf import settings
except ImportError:  # pragma: no cover
    from . import settings


OIDCFED_FEDERATION_WELLKNOWN_URL = ".well-known/openid-federation"
logger = logging.getLogger(__name__)


def jwks_from_jwks_uri(jwks_uri: str, httpc_params: dict = {}) -> list:
    return [json.loads(asyncio.run(http_get([jwks_uri], httpc_params)))] # pragma: no cover


def get_federation_jwks(jwt_payload: dict, httpc_params: dict = {}):
    return (
        jwt_payload.get("jwks", {}).get("keys", [])
    )


def get_http_url(urls: list, httpc_params: dict = {}) -> list:
    if getattr(settings, "HTTP_CLIENT_SYNC", False):
        responses = []
        for i in urls:
            res = requests.get(i, **httpc_params)
            responses.append(res.content.decode())
    else:
        responses = asyncio.run(http_get(urls, httpc_params)) # pragma: no cover
    return responses


def get_entity_statements(urls: list, httpc_params: dict = {}) -> list:
    """
    Fetches an entity statement/configuration
    """
    if isinstance(urls, str):
        urls = [urls] # pragma: no cover
    for url in urls:
        logger.debug(f"Starting Entity Statement Request to {url}")
    return get_http_url(urls, httpc_params)


def get_entity_configurations(subjects: list, httpc_params: dict = {}):
    if isinstance(subjects, str):
        subjects = [subjects]
    urls = []
    for subject in subjects:
        if subject[-1] != "/":
            subject = f"{subject}/"
        url = f"{subject}{OIDCFED_FEDERATION_WELLKNOWN_URL}"
        urls.append(url)
        logger.info(f"Starting Entity Configuration Request for {url}")
    return get_http_url(urls, httpc_params)


class TrustMark:
    def __init__(self, jwt: str, httpc_params: dict = {}):
        self.jwt = jwt
        self.header = unpad_jwt_head(jwt)
        self.payload = unpad_jwt_payload(jwt)

        self.id = self.payload["id"]
        self.sub = self.payload["sub"]
        self.iss = self.payload["iss"]

        self.is_valid = False

        self.issuer_entity_configuration = None
        self.httpc_params = httpc_params

    def validate_by(self, ec) -> bool:
        # TODO: pydantic entity configuration validation here

        if self.header.get("kid") not in ec.kids:
            raise UnknownKid( # pragma: no cover
                f"Trust Mark validation failed: "
                f"{self.header.get('kid')} not found in {ec.jwks}"
            )
        # verify signature
        payload = verify_jws(self.jwt, ec.jwks[ec.kids.index(self.header["kid"])])
        self.is_valid = True
        return payload

    def validate_by_its_issuer(self) -> bool:
        if not self.issuer_entity_configuration:
            self.issuer_entity_configuration = get_entity_configurations(
                self.iss, self.httpc_params
            )
        try:
            ec = EntityConfiguration(self.issuer_entity_configuration[0])
            ec.validate_by_itself()
        except UnknownKid:
            logger.warning(
                f"Trust Mark validation failed by its Issuer: "
                f"{self.header.get('kid')} not found in "
                f"{self.issuer_entity_configuration.jwks}")
            return False
        except Exception:
            logger.warning(f"Issuer {self.iss} of trust mark {self.id} is not valid.")
            self.is_valid = False
            return False

        # verify signature
        payload = verify_jws(
            self.jwt,
            ec.jwks[
                ec.kids.index(self.header["kid"])
            ],
        )
        self.is_valid = True
        return payload

    def __repr__(self) -> str:
        return f"{self.id} to {self.sub} issued by {self.iss}"


class EntityConfiguration:
    """
    The self issued/signed statement of a federation entity
    """

    def __init__(
        self,
        jwt: str,
        httpc_params: dict = {},
        filter_by_allowed_trust_marks: list = [],
        trust_anchor_entity_conf=None,
        trust_mark_issuers_entity_confs: dict = [],
    ):
        self.jwt = jwt
        self.header = unpad_jwt_head(jwt)
        self.payload = unpad_jwt_payload(jwt)
        self.sub = self.payload["sub"]
        self.iss = self.payload["iss"]
        self.jwks = get_federation_jwks(self.payload, httpc_params)
        if not self.jwks[0]:
            _msg = f"Missing jwks in the statement for {self.sub}"
            logger.error(_msg)
            raise MissingJwksClaim(_msg)

        self.kids = [i.get("kid") for i in self.jwks]
        self.httpc_params = httpc_params

        self.filter_by_allowed_trust_marks = filter_by_allowed_trust_marks
        self.trust_anchor_entity_conf = trust_anchor_entity_conf
        self.trust_mark_issuers_entity_confs = trust_mark_issuers_entity_confs

        # a dict with sup_sub : superior entity configuration
        self.verified_superiors = {}
        # as previous but with superiors with invalid entity configurations
        self.failed_superiors = {}

        # a dict with sup_sub : entity statement issued for self
        self.verified_by_superiors = {}
        self.failed_by_superiors = {}

        # a dict with the paylaod of valid entity statements for each descendant subject
        self.verified_descendant_statements = {}
        self.failed_descendant_statements = {}

        # a dict with the RAW JWT of valid entity statements for each descendant subject
        self.verified_descendant_statements_as_jwt = {}

        self.verified_trust_marks = []
        self.is_valid = False

    def validate_by_itself(self) -> bool:
        """
        validates the entity configuration by it self
        """
        # TODO: pydantic entity configuration validation here
        if self.header.get("kid") not in self.kids:
            raise UnknownKid(f"{self.header.get('kid')} not found in {self.jwks}") # pragma: no cover
        # verify signature
        verify_jws(self.jwt, self.jwks[self.kids.index(self.header["kid"])])
        self.is_valid = True
        return True

    def validate_by_allowed_trust_marks(self) -> bool:
        """
        validate the entity configuration ony if marked by a well known
        trust mark, issued by a trusted issuer
        """

        if not self.trust_anchor_entity_conf:
            raise TrustAnchorNeeded(
                "To validate the trust marks the "
                "Trust Anchor Entity Configuration "
                "is needed."
            )

        if not self.filter_by_allowed_trust_marks:
            return True

        if not self.payload.get("trust_marks"):
            logger.warning(
                f"{self.sub} doesn't have the trust marks claim "
                "in its Entity Configuration"
            )
            return False

        trust_marks = []
        is_valid = False
        for tm in self.payload["trust_marks"]:

            if tm.get("id", None) not in self.filter_by_allowed_trust_marks:
                continue

            try:
                trust_mark = TrustMark(tm["trust_mark"])
            except KeyError:
                logger.warning(
                    f"Trust Mark decoding failed on [{tm}]. "
                    "Missing 'trust_mark' claim in it"
                )
            except Exception:
                logger.warning(f"Trust Mark decoding failed on [{tm}]")
                continue
            else:
                trust_marks.append(trust_mark)

        if not trust_marks:
            raise MissingTrustMark("Required Trust marks are missing.") # pragma: no cover

        trust_mark_issuers_by_id = self.trust_anchor_entity_conf.payload.get(
            "trust_marks_issuers", {}
        )

        # TODO : cache of issuers -> it would be better to have a proxy function
        #
        # required_issuer_ecs = []
        # for trust_mark in trust_marks:
        # if trust_mark.iss not in [
        # i.payload.get('iss', None)
        # for i in self.trust_mark_issuers_entity_confs
        # ]:
        # required_issuer_ecs.append(trust_mark.iss)
        # TODO: snippet for CACHE
        # if required_issuer_ec:
        # ## fetch the issuer entity configuration and validate it
        # iecs = get_entity_configurations(
        # [required_issuer_ecs], self.httpc_params
        # )
        # for jwt in iecs:
        # try:
        # ec = self.__class__(jwt, httpc_params=self.httpc_params)
        # ec.validate_by_itself()
        # except Exception as e:
        # logger.warning(
        # "Trust Marks issuer Entity Configuration "
        # f"failed for {jwt}: {e}"
        # )
        # continue
        # self.trust_mark_issuers_entity_confs.append(ec)

        for trust_mark in trust_marks:
            id_issuers = trust_mark_issuers_by_id.get(trust_mark.id, None)
            if id_issuers and trust_mark.iss not in id_issuers:
                is_valid = False
            elif id_issuers and trust_mark.iss in id_issuers:
                is_valid = trust_mark.validate_by_its_issuer()
            elif not id_issuers:
                is_valid = trust_mark.validate_by(self.trust_anchor_entity_conf)

            if not trust_mark.is_valid:
                is_valid = False

            if is_valid:
                logger.info(f"Trust Mark {trust_mark} is valid")
                self.verified_trust_marks.append(trust_mark)
            else:
                logger.warning(f"Trust Mark {trust_mark} is not valid")

        return is_valid

    def get_superiors(
        self,
        authority_hints: list = [],
        max_authority_hints: int = 0,
        superiors_hints: list = [],
    ) -> dict:
        """
        get superiors entity configurations
        """
        # apply limits if defined
        authority_hints = authority_hints or deepcopy(self.payload.get("authority_hints", []))
        if (
            max_authority_hints
            and authority_hints != authority_hints[:max_authority_hints]
        ):
            logger.warning(
                f"Found {len(authority_hints)} but "
                f"authority maximum hints is set to {max_authority_hints}. "
                "the following authorities will be ignored: "
                f"{', '.join(authority_hints[max_authority_hints:])}"
            )
            authority_hints = authority_hints[:max_authority_hints]

        for sup in superiors_hints:
            if sup.sub in authority_hints:
                logger.info(
                    "Getting Cached Entity Configurations for "
                    f"{[i.sub for i in superiors_hints]}"
                )
                authority_hints.pop(authority_hints.index(sup.sub))
                self.verified_superiors[sup.sub] = sup

        logger.debug(f"Getting Entity Configurations for {authority_hints}")

        jwts = get_entity_configurations(authority_hints, self.httpc_params)
        for jwt in jwts:
            try:
                ec = self.__class__(jwt, httpc_params=self.httpc_params)
            except Exception as e:
                logger.warning(f"Get Entity Configuration for {jwt}: {e}")
                continue

            if ec.validate_by_itself():
                target = self.verified_superiors
            else:
                target = self.failed_superiors

            target[ec.payload["sub"]] = ec

        for ahints in authority_hints:
            if not self.verified_superiors.get(ahints, None):
                logger.warning(
                    f"{ahints} is not available, missing or not valid authority hint"
                )
                continue

        return self.verified_superiors

    def validate_descendant_statement(self, jwt: str) -> bool:
        """
        jwt is a descendant entity statement issued by self
        """
        # TODO: pydantic entity configuration validation here
        header = unpad_jwt_head(jwt)
        payload = unpad_jwt_payload(jwt)

        if header.get("kid") not in self.kids:
            raise UnknownKid(f"{self.header.get('kid')} not found in {self.jwks}")
        # verify signature
        payload = verify_jws(jwt, self.jwks[self.kids.index(header["kid"])])

        self.verified_descendant_statements[payload["sub"]] = payload
        self.verified_descendant_statements_as_jwt[payload["sub"]] = jwt
        return self.verified_descendant_statements

    def validate_by_superior_statement(self, jwt: str, ec):
        """
        jwt is a statement issued by a superior
        ec is a superior entity configuration

        this method validates self with the jwks contained in statement
        of the superior
        """
        is_valid = None
        payload = {}
        try:
            payload = unpad_jwt_payload(jwt)
            ec.validate_by_itself()
            ec.validate_descendant_statement(jwt)
            _jwks = get_federation_jwks(payload, self.httpc_params)
            _kids = [i.get("kid") for i in _jwks]
            verify_jws(self.jwt, _jwks[_kids.index(self.header["kid"])])
            is_valid = True
        except Exception as e:
            logger.warning(
                f"{self.sub} failed validation with "
                f"{ec.sub}'s superior statement '{payload or jwt}'. "
                f"Exception: {e}"
            )
            is_valid = False

        if is_valid:
            target = self.verified_by_superiors
            ec.verified_descendant_statements[self.sub] = payload
            ec.verified_descendant_statements_as_jwt[self.sub] = jwt
            target[payload["iss"]] = ec
            self.is_valid = True
            return self.verified_by_superiors.get(ec.sub)
        else:
            target = self.failed_superiors
            ec.failed_descendant_statements[self.sub] = payload
            self.is_valid = False

    def validate_by_superiors(
        self,
        superiors_entity_configurations: dict = {},
    ):  # -> dict[str, EntityConfiguration]:
        """
        validates the entity configuration with the entity statements
        issued by its superiors

        this methods create self.verified_superiors and failed ones
        and self.verified_by_superiors and failed ones
        """
        for ec in superiors_entity_configurations:
            if ec.sub in ec.verified_by_superiors:
                # already fetched and cached
                continue

            try:
                # get superior fetch url
                fetch_api_url = ec.payload["metadata"]["federation_entity"][
                    "federation_fetch_endpoint"
                ]
            except KeyError:
                logger.warning(
                    "Missing federation_fetch_endpoint in  "
                    f"federation_entity metadata for {self.sub} by {ec.sub}."
                )
                self.failed_superiors[ec.sub] = None
                continue

            else:
                _url = f"{fetch_api_url}?sub={self.sub}"
                logger.info(f"Getting entity statements from {_url}")
                jwts = get_entity_statements([_url], self.httpc_params)
                jwt = jwts[0]
                self.validate_by_superior_statement(jwt, ec)

        return self.verified_by_superiors

    def __repr__(self) -> str:
        return f"{self.sub} valid {self.is_valid}"
