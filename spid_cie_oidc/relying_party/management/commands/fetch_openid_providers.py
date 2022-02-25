import json

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from spid_cie_oidc.entity.trust_chain_operations import get_or_create_trust_chain


class Command(BaseCommand):
    help = 'Attribute release query'

    def add_arguments(self, parser):
        parser.epilog = 'Example: ./manage.py fetch_openid_providers'
        parser.add_argument(
            '--start', required=True,
            help=_(
                "Collect a trust chains for each openid_provider defined in "
                "settings.OIDCFED_IDENTITY_PROVIDERS"
            )
        )
        parser.add_argument('-debug', required=False, action="store_true",
                            help="see debug message")

    def handle(self, *args, **options):
        if not options['start']:
            return

        res = []
        for op_sub in settings.OIDCFED_IDENTITY_PROVIDERS:
            tc = get_or_create_trust_chain(
                subject = op_sub,
                trust_anchor = settings.FEDERATION_TRUST_ANCHOR,
                metadata_type = 'openid_provider',
                httpc_params = settings.HTTPC_PARAMS,
                required_trust_marks = getattr(
                    settings, 'OIDCFED_REQUIRED_TRUST_MARKS', []
                )
            )
            res.append(tc)
        
