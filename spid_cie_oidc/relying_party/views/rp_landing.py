import logging
import random

from django.conf import settings
from django.shortcuts import render
from spid_cie_oidc.entity.models import TrustChain

logger = logging.getLogger(__name__)


def oidc_rp_landing(request):
    spid_providers = []
    cie_providers = []

    for s in settings.OIDCFED_IDENTITY_PROVIDERS.get("spid", []):
        t = TrustChain.objects.filter(
            sub = s,
            metadata__openid_provider__isnull=False,
            is_active=True
        )
        provider = dict(trust = t.first())
        spid_providers.append(provider)
            
    for c in settings.OIDCFED_IDENTITY_PROVIDERS.get("cie", []):
        t = TrustChain.objects.filter(
            sub = c,
            metadata__openid_provider__isnull=False,
            is_active=True
        )
        provider = dict(trust = t.first())
        cie_providers.append(provider)

    random.shuffle(spid_providers)
    content = {
        "spid_providers": spid_providers,
        "cie_providers" : cie_providers
    }
    return render(request, "rp_landing.html", content)
