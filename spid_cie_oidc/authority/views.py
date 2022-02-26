from django.http import Http404
from django.http import HttpResponse
from django.http import JsonResponse

from spid_cie_oidc.authority.models import (
    FederationDescendant,
    FederationEntityAssignedProfile,
    get_first_self_trust_anchor,
)
from spid_cie_oidc.entity.jwtse import create_jws, unpad_jwt_payload
from spid_cie_oidc.entity.models import TrustChain
from spid_cie_oidc.entity.settings import HTTPC_PARAMS
from spid_cie_oidc.entity.trust_chain_operations import get_or_create_trust_chain


def fetch(request):
    if request.GET.get("iss"):
        iss = get_first_self_trust_anchor(sub=request.GET["iss"])
    else:
        iss = get_first_self_trust_anchor()

    if not request.GET.get("sub"):
        conf = get_first_self_trust_anchor()
        if request.GET.get("format") == "json":
            return JsonResponse(conf.entity_configuration_as_dict, safe=False)
        else:
            return HttpResponse(
                conf.entity_configuration_as_jws, content_type="application/jose"
            )

    sub = FederationDescendant.objects.filter(
        sub=request.GET["sub"], is_active=True
    ).first()
    if not sub:
        raise Http404()

    if request.GET.get("format") == "json":
        return JsonResponse(
            sub.entity_statement_as_dict(iss.sub, request.GET.get("aud")), safe=False
        )
    else:
        return HttpResponse(
            sub.entity_statement_as_jws(iss.sub, request.GET.get("aud")),
            content_type="application/jose",
        )


def entity_list(request):
    is_leaf = request.GET.get("is_leaf", "").lower()
    if is_leaf == "true":
        _q = {
            "profile__profile_category__in": ("openid_relying_party", "openid_provider")
        }
    elif is_leaf == "false":
        _q = {"profile__profile_category": "federation_entity"}
    elif request.GET.get("type", "").lower():
        _q = {"profile__profile_category": request.GET["type"]}
    else:
        _q = {}

    entries = FederationEntityAssignedProfile.objects.filter(**_q).values_list(
        "descendant__sub", flat=True
    )
    return JsonResponse(list(set(entries)), safe=False)


def resolve_entity_statement(request):
    """
    resolves the final metadata of its descendants

    In this implementation we only returns a preexisting
    Metadata if it's valid
    we avoid any possibility to trigger a new Metadata discovery if
    """
    if not all(
        (
            request.GET.get("sub", None),
            request.GET.get("anchor", None)
        )
    ):
        raise Http404("sub and anchor parameters are REQUIRED.")

    if request.GET.get('iss'):
        iss = get_first_self_trust_anchor(sub = request.GET['iss'])
    else:
        iss = get_first_self_trust_anchor()

    _q = dict(
        sub=request.GET["sub"],
        trust_anchor__sub=request.GET["anchor"]
    )
    if request.GET.get("type", None):
        _q['type'] = request.GET["type"]

    entity = TrustChain.objects.filter(**_q).first()
    if entity and not entity.is_active:
        raise Http404("entity not found.")
    else:
        get_or_create_trust_chain(
            httpc_params = HTTPC_PARAMS,
            # TODO
            # required_trust_marks = [],
            subject = _q['sub'],
            trust_anchor = _q['trust_anchor__sub']
        )
        entity = TrustChain.objects.filter(**_q).first()

    if not entity:
        raise Http404("entity not found.")

    res = {
      "iss": iss.sub,
      "sub": request.GET["sub"],
      # "aud": [],
      "iat": entity.iat_as_timestamp,
      "exp": entity.exp_as_timestamp,
      "trust_marks": [],
      "metadata": entity.metadata
    }

    if request.GET.get("format") == "json":
        return JsonResponse(res, safe=False)
    else:
        return HttpResponse(
            create_jws(res, iss.jwks[0]),
            content_type="application/jose",
        )
    

def trust_mark_status(request):

    if request.GET.get('sub', "") and request.GET.get('id', ""):
        sub = request.GET["sub"]
        _id = request.GET["id"]

    elif request.GET.get('trust_mark', ""):
        payload = unpad_jwt_payload(request.GET['trust_mark'])
        sub = payload.get('sub', "")
        _id = payload.get('id', "")

    res = FederationEntityAssignedProfile.objects.filter(
        descendant__sub = sub,
        profile__profile_id = _id,
        descendant__is_active = True
    )
    if res:
        return JsonResponse({"active": True})
    else:
        return JsonResponse({"active": False})
