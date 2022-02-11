from django.shortcuts import render

from spid_cie_oidc.entity.models import FederationEntityConfiguration
from spid_cie_oidc.onboarding.models import FederationDescendant
from spid_cie_oidc.entity.views import entity_configuration
from spid_cie_oidc.entity.jwtse import create_jws

from . models import 


def fetch(request):
    if request.GET.get('iss'):
        iss = FederationEntityConfiguration.objects.filter(
            sub = request.GET['iss'], is_active=True
        ).first()
    else:
        iss = FederationEntityConfiguration.objects.filter(
            metadata__federation_entity__isnull=False,
            is_null=False
        ).first()

    if not request.GET.get('sub'):
        return entity_configuration(request)

    sub = FederationDescendant.objects.filter(
        sub=sub, is_active=True
    ).first()

    if request.GET.get('format') == 'json':
        return JsonResponse(sub.entity_statement_as_json, safe=False)
    else:
        jws = create_jws(
            sub.entity_statement, iss.jwks[0], alg=iss.default_signature_alg
        )
        return HttpResponse(
            jws, content_type="application/jose"
        )
