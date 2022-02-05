from django.shortcuts import render
from django.http import HttpResponse

from . models import FederationAuthorityConfiguration
from . jwtse import create_jws


def entity_configuration(request):
    """
        OIDC Federation Entity Configuration at
        .well-known/openid-federation
    """
    conf = FederationAuthorityConfiguration.objects.filter(
        is_active=True
    ).first()
    jws = create_jws(
        conf.entity_configuration, conf.jwks[0], alg=conf.default_signature_alg
    )
    return HttpResponse(
        jws, content_type="application/jose"
    )


def fetch(request):
    return HttpResponse('not implemented')
