from django.http import Http404
from django.http import HttpResponse
from django.http import JsonResponse

from django.shortcuts import render

from spid_cie_oidc.entity.models import FederationEntityConfiguration
from spid_cie_oidc.entity.policy import apply_policy
from spid_cie_oidc.onboarding.models import (
    FederationDescendant,
    FederationEntityAssignedProfile,
    get_first_self_trust_anchor
)
from spid_cie_oidc.entity.jwtse import create_jws

from . models import (
    FederationDescendant,
    get_first_self_trust_anchor
)


def fetch(request):
    if request.GET.get('iss'):
        iss = get_first_self_trust_anchor(sub = request.GET['iss'])
    else:
        iss = get_first_self_trust_anchor()

    if not request.GET.get('sub'):
        conf = get_first_self_trust_anchor()
        if request.GET.get('format') == 'json':
            return JsonResponse(
                conf.entity_configuration_as_dict, safe=False
            )
        else:
            return HttpResponse(
                conf.entity_configuration_as_jws,
                content_type="application/jose"
            )

    sub = FederationDescendant.objects.filter(
        sub=request.GET['sub'], is_active=True
    ).first()
    if not sub:
        raise Http404()

    if request.GET.get('format') == 'json':
        return JsonResponse(sub.entity_statement_as_dict, safe=False)
    else:
        return HttpResponse(
            sub.entity_statement_as_jws, content_type="application/jose"
        )


def entity_list(request):
    if request.GET.get('is_leaf') == 'true':
        _q = {'profile__profile_category__in' : (
                'openid_relying_party', 'openid_provider'
            )}
    elif request.GET.get('is_leaf') == 'false':
        _q = {'profile__profile_category' : 'federation_entity'}
    else:
        _q = {}

    entries = FederationEntityAssignedProfile.objects.filter(**_q).values_list('descendant__sub', flat=True)
    return JsonResponse(list(entries), safe=False)


def resolve_entity_statement(request):
    """
        resolves the final metadata of its descendants
    """
    if not all(
        request.GET.get('sub'),
        request.GET.get('anchor'),
    ):
        raise Http404("sub and anchor parameters are REQUIRED.")

    # TODO: resolve also other entities in a federation
    # TODO: release a metadata on top of a resolved trust chain
    if request.GET.get('iss'):
        iss = get_first_self_trust_anchor(sub = request.GET['iss'])
    else:
        iss = get_first_self_trust_anchor()
    
    entity = FederationDescendant.objects.filter(
        sub = request.GET['sub'], is_active = True
    )

    # filter by type
    if request.GET.get('type'):
        policy = entity.metadata_policy.get(request.GET['type'])
        #metadata = 
