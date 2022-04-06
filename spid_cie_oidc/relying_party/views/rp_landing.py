from copy import deepcopy
import logging
import random


from django.conf import settings
from django.shortcuts import render
from spid_cie_oidc.entity.trust_chain_operations import get_or_create_trust_chain

logger = logging.getLogger(__name__)


def oidc_rp_landing(request):
    spid_providers = {
        k: {"sub": v} for k, v in
        settings.OIDCFED_IDENTITY_PROVIDERS.get("spid", {}).items()
    }
    cie_providers = {
        k: {"sub": v} for k, v in
        settings.OIDCFED_IDENTITY_PROVIDERS.get("cie", {}).items()
    }

    providers = deepcopy(spid_providers)
    providers.update(cie_providers)
    subs = list(spid_providers.keys()) + list(cie_providers.keys())

    tcs = []
    for sub in subs:
        try:
            tc = get_or_create_trust_chain(
                subject = sub,
                trust_anchor = providers[sub]["sub"]
            )
            tcs.append(tc)
        except Exception as e:
            logger.warning(
                f"Failed trust chain for {sub} to {providers[sub]}: {e}"
            )

    for i in tcs:
        if i.sub in settings.OIDCFED_IDENTITY_PROVIDERS.get("spid", {}):
            target = spid_providers
        elif i.sub in settings.OIDCFED_IDENTITY_PROVIDERS.get("cie", {}):
            target = cie_providers
        else:
            continue

        target[i.sub] = {
            "sub": i.sub,
            "logo_uri" : i.metadata.get("openid_provider", {}).get("logo_uri", ""),
            "organization_name": i.metadata.get("openid_provider", {}).get("organization_name","")
        }

    s_spid_providers = list(spid_providers.items())
    random.shuffle(s_spid_providers)
    content = {
        "spid_providers": dict(s_spid_providers),
        "cie_providers" : cie_providers
    }
    return render(request, "rp_landing.html", content)
