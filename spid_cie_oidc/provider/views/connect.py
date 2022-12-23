import logging

from djagger.decorators import schema
from django.http import Http404
from django.http import JsonResponse

from spid_cie_oidc.entity.models import FederationEntityConfiguration
logger = logging.getLogger(__name__)


@schema(
    summary="OIDC Provider openid-configuration",
    methods=['GET'],
    tags = ['Provider']
)
def openid_configuration(request):
    """
    OIDC Discovery configuration at
    .well-known/openid-connect
    """
    _sub = request.build_absolute_uri().split(".well-known/openid-configuration")[0]
    conf = FederationEntityConfiguration.objects.filter(
        # TODO: check for reverse proxy and forwarders ...
        sub=_sub,
        is_active=True,
    ).first()
    if not conf: # pragma: no cover
        raise Http404()
    
    content = conf.entity_configuration_as_dict['metadata'].get('openid_provider', None)
    if content:
        return JsonResponse(content, safe=False)
    else:
        raise Http404()
