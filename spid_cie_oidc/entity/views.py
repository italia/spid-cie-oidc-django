from django.http import HttpResponse
from django.http import JsonResponse

from . models import FederationEntityConfiguration
from . jwtse import create_jws


def entity_configuration(request):
    """
        OIDC Federation Entity Configuration at
        .well-known/openid-federation
    """
    conf = FederationEntityConfiguration.objects.filter(
        is_active=True
    ).first()
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
