import logging
import math
import urllib.parse

from djagger.decorators import schema
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
    FederationEntityAssignedProfile
)
from spid_cie_oidc.authority.settings import MAX_ENTRIES_PAGE
from spid_cie_oidc.entity.jwtse import (
    unpad_jwt_head, unpad_jwt_payload
)
from spid_cie_oidc.entity.models import get_first_self_trust_anchor
from spid_cie_oidc.entity.utils import iat_now

from . schemas.fetch_endpoint_request import FetchRequest, FedAPIErrorResponse, FetchResponse
from . schemas.list_endpoint import ListRequest, ListResponse
from . schemas.advanced_entity_list_endpoint import AdvancedEntityListRequest, AdvancedEntityListResponse
from . schemas.trust_mark_status_endpoint import TrustMarkRequest, TrustMarkResponse

logger = logging.getLogger(__name__)


@schema(
    methods=['GET'],
    get_request_schema = {
        "application/x-www-form-urlencoded": FetchRequest
    },
    get_response_schema = {
            "400": FedAPIErrorResponse,
            "404": FedAPIErrorResponse,
            "200": FetchResponse
    },
    tags = ['Federation API']
)
def fetch(request):
    """
    All entities that are expected to publish entity statements
    about other entities MUST expose a Fetch endpoint.

    Fetching entity statements is performed to collect entity statements
    one by one to gather trust chains.

    To fetch an entity statement, an entity needs to know the identifier
    of the entity to ask (the issuer), the fetch endpoint of that entity
    and the identifier of the entity that you want the statement to be about (the subject).
    """
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
                conf.entity_configuration_as_jws,
                content_type="application/entity-statement+jwt"
            )

    sub = FederationDescendant.objects.filter(
        sub=request.GET["sub"], is_active=True
    ).first()
    if not sub:
        raise Http404()

    if request.GET.get("format") == "json":
        return JsonResponse(
            sub.entity_statement_as_dict(iss.sub, request.GET.get("aud",[])), safe=False
        )
    else:
        return HttpResponse(
            sub.entity_statement_as_jws(iss.sub, request.GET.get("aud",[])),
            content_type="application/entity-statement+jwt",
        )


@schema(
    methods=['GET'],
    get_request_schema = {
        "application/x-www-form-urlencoded": ListRequest
    },
    get_response_schema = {
            "400": FedAPIErrorResponse,
            "404": FedAPIErrorResponse,
            "200": ListResponse
    },
    tags = ['Federation API']
)
def entity_list(request):
    if request.GET.get("entity_type", "").lower():
        _q = {"profile__profile_category": request.GET["entity_type"]}
    else:
        _q = {}

    entries = FederationEntityAssignedProfile.objects.filter(**_q).values_list(
        "descendant__sub", flat=True
    )
    return JsonResponse(list(set(entries)), safe=False)


@schema(
    methods=['GET'],
    get_request_schema = {
        "application/x-www-form-urlencoded": AdvancedEntityListRequest
    },
    get_response_schema = {
            "400": FedAPIErrorResponse,
            "404": FedAPIErrorResponse,
            "200": AdvancedEntityListResponse
    },
    tags = ['Federation API']
)
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


@schema(
    methods=['GET'],
    get_request_schema = {
        "application/x-www-form-urlencoded": TrustMarkRequest
    },
    get_response_schema = {
            "400": FedAPIErrorResponse,
            "404": FedAPIErrorResponse,
            "200": TrustMarkResponse
    },
    tags = ['Federation API']
)
def trust_mark_status(request):
    failed_data = {"active": False}
    if request.POST.get("sub", "") and request.POST.get("id", ""):
        sub = request.POST["sub"]
        _id = request.POST["id"]

    elif request.POST.get("trust_mark", ""):
        try:
            unpad_jwt_head(request.POST["trust_mark"])
            payload = unpad_jwt_payload(request.POST["trust_mark"])
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
