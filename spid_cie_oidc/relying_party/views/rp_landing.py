import logging
import random

from django.conf import settings
from django.shortcuts import render
from spid_cie_oidc.entity.models import TrustChain

logger = logging.getLogger(__name__)


def oidc_rp_landing(request):
    trust_chains = TrustChain.objects.filter(
        metadata__openid_provider__isnull=False,
        is_active=True
    )
    spid_providers = []
    cie_providers = []
    for tc in trust_chains:
        if tc.is_active:
            if tc.sub in settings.OIDCFED_IDENTITY_PROVIDERS.get("spid", []):
                spid_providers.append(tc)
            elif tc.sub in settings.OIDCFED_IDENTITY_PROVIDERS.get("cie", []):
                cie_providers.append(tc)
    random.shuffle(spid_providers)
    content = {
        "spid_providers": spid_providers,
        "cie_providers" : cie_providers
    }
    return render(request, "rp_landing.html", content)
