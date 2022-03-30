import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from spid_cie_oidc.entity.settings import HTTPC_PARAMS
from spid_cie_oidc.entity.trust_chain_operations import get_or_create_trust_chain


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Attribute release query"

    def add_arguments(self, parser):
        parser.epilog = "Example: ./manage.py fetch_openid_providers"
        parser.add_argument(
            "--start",
            action="store_true",
            required=True,
            help=_(
                "Collect a trust chains for each openid_provider defined in "
                "settings.OIDCFED_IDENTITY_PROVIDERS"
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
        if not options["start"]:
            return # pragma: no cover

        res = []
        for op_profile in settings.OIDCFED_IDENTITY_PROVIDERS.keys():
            for op_sub, ta in settings.OIDCFED_IDENTITY_PROVIDERS[op_profile].items():
                logger.info(f"Fetching Entity Configuration for {op_sub}")
                try:
                    tc = get_or_create_trust_chain(
                        subject=op_sub,
                        trust_anchor=ta,
                        httpc_params=HTTPC_PARAMS,
                        required_trust_marks=getattr(
                            settings, "OIDCFED_REQUIRED_TRUST_MARKS", []
                        ),
                        force=options["force"],
                    )
                    if tc.is_valid:
                        res.append(tc)

                    logger.info(f"Final Metadata for {tc.sub}:\n\n{tc.metadata}")

                except Exception as e:
                    logger.error(f"Failed to download {op_sub} due to: {e}")
                    continue

        logger.info(f"Found {res}")
