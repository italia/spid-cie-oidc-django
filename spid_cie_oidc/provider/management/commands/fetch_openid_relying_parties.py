import json
import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from spid_cie_oidc.entity.statements import (
    get_entity_configurations,
    get_http_url,
    EntityConfiguration,
)
from spid_cie_oidc.entity.trust_chain_operations import get_or_create_trust_chain


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Attribute release query"

    def add_arguments(self, parser):
        parser.epilog = "Example: ./manage.py fetch_openid_providers"
        parser.add_argument(
            "--from",
            nargs="*",
            default=[],
            help=_(
                "A list of url of authorities, separated by space where "
                "download the list of OPs"
            ),
        )
        parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            required=False,
            help=_("Don't use already cached statements and chains"),
        )
        parser.add_argument(
            "-debug", required=False, action="store_true", help="see debug message"
        )

    def handle(self, *args, **options):
        if not options["from"]:
            return # pragma: no cover

        res = []
        rp_subs = []
        jwts = get_entity_configurations(options["from"])
        auth_ecs = []
        for i in jwts:
            ec = EntityConfiguration(i)
            if ec.validate_by_itself():
                auth_ecs.append(ec)

        if not auth_ecs:
            logger.warning(
                f"Any of {options['from']} has a valid EntityConfiguration "
                "to get a List endpoint"
            )
            return

        logger.info(
            f"Found {auth_ecs} federation entities where to query a list of RPs"
        )

        list_urls = []
        for i in auth_ecs:
            endpoint = (
                i.payload.get("metadata", {})
                .get("federation_entity", {})
                .get("federation_list_endpoint", "")
            )
            if endpoint:
                list_urls.append(f"{endpoint}?type=openid_relying_party")

        rp_subs = []
        for rp_sub in get_http_url(list_urls, httpc_params=settings.HTTPC_PARAMS):

            try:
                urls = json.loads(rp_sub)
                rp_subs.extend(urls)
            except Exception as e:
                logger.error(f"Failed {e}")
                continue

        for rp_sub in rp_subs:
            try:
                tc = get_or_create_trust_chain(
                    subject=rp_sub,
                    trust_anchor=settings.OIDCFED_DEFAULT_TRUST_ANCHOR,
                    metadata__relying_party__is_null=False,
                    httpc_params=settings.HTTPC_PARAMS,
                    required_trust_marks=getattr(
                        settings, "OIDCFED_REQUIRED_TRUST_MARKS", []
                    ),
                    force=options["force"],
                )
                if tc.is_valid:
                    res.append(tc)

                logger.info(f"Final Metadata for {tc.sub}:\n\n{tc.metadata}")

            except Exception as e:
                logger.exception(f"Failed to download {rp_sub} due to: {e}")
