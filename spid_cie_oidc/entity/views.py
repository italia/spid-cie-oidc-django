from django.http import Http404
from django.http import HttpResponse
from django.http import JsonResponse

from . models import FederationEntityConfiguration
from . jwtse import create_jws


def entity_configuration(request):
    """
        OIDC Federation Entity Configuration at
        .well-known/openid-federation
    """
    _sub = request.build_absolute_uri().split(
        '.well-known/openid-federation'
    )[0]
    conf = FederationEntityConfiguration.objects.filter(
        # TODO: check for reverse proxy and forwarders ...
        sub = _sub, 
        is_active=True
    ).first()

    if not conf:
        raise Http404()
    
    jws = create_jws(
        conf.entity_configuration, conf.jwks[0], alg=conf.default_signature_alg
    )
    if request.GET.get('format') == 'json':
        return JsonResponse(conf.raw_entity_configuration, safe=False)
    else:
        return HttpResponse(
            jws, content_type="application/jose"
        )


def fetch(request):
    return HttpResponse('not implemented')
