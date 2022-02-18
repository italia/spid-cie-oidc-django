from django.test import Client
from django.urls import reverse

from spid_cie_oidc.entity.models import FederationEntityConfiguration
from spid_cie_oidc.entity.jwtse import unpad_jwt_payload
from spid_cie_oidc.entity.tests.settings import ta_conf_data
from . settings import rp_onboarding_data

import logging
logger = logging.getLogger(__name__)


class DummyContent:
    def __init__(self, content):
        self.content = content.encode()


class EntityResponse:
    def __init__(self):
        self.status_code = 200
        self.req_counter = 0
        self.client = Client()

    @property
    def content(self):
        if self.req_counter == 0:
            url = reverse('entity_configuration')
            res = self.client.get(url, data={'sub': ta_conf_data['sub']})
        elif self.req_counter == 1:
            rp = FederationEntityConfiguration.objects.get(sub=rp_onboarding_data['sub'])
            res = DummyContent(rp.entity_configuration_as_jws)
        elif self.req_counter == 2:
            url = reverse('entity_configuration')
            res = self.client.get(url, data={'sub': ta_conf_data['sub']})
        elif self.req_counter == 3:
            url = reverse('oidcfed_fetch')
            res = self.client.get(url, data={'sub': rp_onboarding_data['sub']})

        self.req_counter += 1
        logger.info(unpad_jwt_payload(res.content.decode()))
        return res.content
