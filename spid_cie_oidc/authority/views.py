import logging
import math
import urllib.parse

from django.conf import settings
from django.core.paginator import Paginator
from django.http import (
    Http404,
    HttpResponse,
    JsonResponse
)
from django.urls import reverse

from spid_cie_oidc.authority.models import (
    FederationDescendant,
    FederationEntityAssignedProfile,
    get_first_self_trust_anchor
)
from spid_cie_oidc.authority.settings import MAX_ENTRIES_PAGE
from spid_cie_oidc.entity.jwtse import (
    create_jws, unpad_jwt_head,
    unpad_jwt_payload
)
from spid_cie_oidc.entity.models import TrustChain
from spid_cie_oidc.entity.settings import HTTPC_PARAMS
from spid_cie_oidc.entity.trust_chain_operations import get_or_create_trust_chain
from spid_cie_oidc.entity.utils import iat_now


logger = logging.getLogger(__name__)


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
                conf.entity_configuration_as_jws, content_type="application/entity-statement+jwt"
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
            content_type="application/entity-statement+jwt",
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


def advanced_entity_listing(request):
    desecendants = FederationDescendant.objects.filter(
        is_active = True,
    ).order_by("-modified")
    entities_list = []
    for descendant in desecendants:
        entity = {
            descendant.sub : {
                "iat" : int(descendant.modified.timestamp())
            }
        }
        entities_list.append(entity)
    total_entries = desecendants.count()

    _max_entries = getattr(settings, 'MAX_ENTRIES_PAGE', MAX_ENTRIES_PAGE)
    p = Paginator(entities_list, _max_entries)
    page = request.GET.get("page", 1)
    entities = p.get_page(page)
    next_page_path = ""
    if entities.has_next():
        param = {"page": entities.next_page_number()}
        url = f'{reverse("oidcfed_advanced_entity_listing")}?{urllib.parse.urlencode(param)}'
        next_page_path = f"{url}"
    prev_page_path = ""
    if entities.has_previous():
        param = {"page": entities.previous_page_number()}
        url = f'{reverse("oidcfed_advanced_entity_listing")}?{urllib.parse.urlencode(param)}'
        prev_page_path = f"{url}"
    try:
        iss = get_first_self_trust_anchor().sub
    except Exception:
        return JsonResponse(
            {
                "error": "Missing trust anchor",
            },
            status = 404
        )
    res = {
            "iss" : iss,
            "iat" : iat_now(),
            "entities" : entities_list,
            "page" : int(page),
            "total_pages" : math.ceil(total_entries / MAX_ENTRIES_PAGE),
            "total_entries" : total_entries,
            "next_page_path": next_page_path,
            "prev_page_path": prev_page_path,
    }
    return JsonResponse(res, safe=False)


def resolve_entity_statement(request, format: str = "jose"):
    """
    resolves the final metadata of its descendants

    In this implementation we only returns a preexisting
    Metadata if it's valid
    we avoid any possibility to trigger a new Metadata discovery if
    """
    if not all((request.GET.get("sub", None), request.GET.get("anchor", None))):
        raise Http404("sub and anchor parameters are REQUIRED.")

    if request.GET.get("iss"):
        iss = get_first_self_trust_anchor(sub=request.GET["iss"])
    else:
        iss = get_first_self_trust_anchor()

    _q = dict(
        sub=request.GET["sub"],
        trust_anchor__sub=request.GET["anchor"],
        is_active=True
    )
    entity = TrustChain.objects.filter(**_q)

    if not entity:
        raise Http404("entity not found.")
    elif entity and request.GET.get("type", None):
        _q["type"] = request.GET["type"]
        typed_entity = entity.filter(type=request.GET["type"]).first()
        if not typed_entity:
            logger.warning(
                f'Resolve statement endpoint not found for {request.GET["sub"]} '
                f'with metadata_type {request.GET["type"]}.'
            )
            raise Http404("entity metadata type not found.")
        else:
            entity = typed_entity

    try:
        tc_data = dict(
            httpc_params=HTTPC_PARAMS,
            # TODO
            # required_trust_marks = [],
            subject=_q["sub"],
            trust_anchor=_q["trust_anchor__sub"]
        )
        if _q.get('type', None):
            tc_data["metadata_type"] = _q['type']
        entity = get_or_create_trust_chain(**tc_data)
    except Exception as e:
        logger.error(
            f"Failed Trust Chain on resolve statement endpoint: {e}"
        )
        raise Http404("entity not found.")

    res = {
        "iss": iss.sub,
        "sub": request.GET["sub"],
        # "aud": [],
        "iat": entity.iat_as_timestamp,
        "exp": entity.exp_as_timestamp,
        "trust_marks": entity.trust_marks,
        "metadata": entity.metadata,
    }

    if request.GET.get("format") == "json" or format == "json":
        return JsonResponse(res, safe=False)
    else:
        return HttpResponse(
            create_jws(res, iss.jwks[0]),
            content_type="application/jose",
        )


def trust_mark_status(request):
    failed_data = {"active": False}
    if request.GET.get("sub", "") and request.GET.get("id", ""):
        sub = request.GET["sub"]
        _id = request.GET["id"]

    elif request.GET.get("trust_mark", ""):
        try:
            unpad_jwt_head(request.GET["trust_mark"])
            payload = unpad_jwt_payload(request.GET["trust_mark"])
            sub = payload.get("sub", "")
            _id = payload.get("id", "")
        except Exception:
            return JsonResponse(failed_data)
    else:
        return JsonResponse(failed_data)

    res = FederationEntityAssignedProfile.objects.filter(
        descendant__sub=sub, profile__profile_id=_id, descendant__is_active=True
    )
    if res:
        return JsonResponse({"active": True})
    else:
        return JsonResponse(failed_data)
