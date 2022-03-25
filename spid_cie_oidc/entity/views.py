from django.http import Http404
from django.http import HttpResponse
from django.http import JsonResponse

from .models import FederationEntityConfiguration
from .statements import OIDCFED_FEDERATION_WELLKNOWN_URL


def entity_configuration(request):
    """
    OIDC Federation Entity Configuration at
    .well-known/openid-federation
    """
    _sub = request.build_absolute_uri().split(OIDCFED_FEDERATION_WELLKNOWN_URL)[0]
    conf = FederationEntityConfiguration.objects.filter(
        # TODO: check for reverse proxy and forwarders ...
        sub=_sub,
        is_active=True,
    ).first()

    if not conf: # pragma: no cover
        raise Http404()

    if request.GET.get("format") == "json": # pragma: no cover
        return JsonResponse(conf.entity_configuration_as_dict, safe=False)
    else:
        return HttpResponse(
            conf.entity_configuration_as_jws, content_type="application/entity-statement+jwt"
        )
