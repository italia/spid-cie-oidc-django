from django.test import Client
from django.urls import reverse

from spid_cie_oidc.entity.models import FederationEntityConfiguration
from spid_cie_oidc.entity.jwtse import unpad_jwt_payload
from spid_cie_oidc.entity.exceptions import HttpError
from spid_cie_oidc.entity.tests.settings import ta_conf_data
from . settings import rp_onboarding_data, intermediary_conf

import json
import logging
logger = logging.getLogger(__name__)


class DummyContent:
    def __init__(self, content):
        self.content = content.encode()
        self.status_code = 200


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
            url = reverse('oidcfed_fetch')
            res = self.client.get(url, data={'sub': rp_onboarding_data['sub']})
        elif self.req_counter > 2:
            raise NotImplementedError(
                "The mocked resposes seems to be not aligned with the correct flow"
            )
        
        self.req_counter += 1
        logger.info(unpad_jwt_payload(res.content.decode()))
        return res.content


class IntermediateEntityResponse(EntityResponse):

    @property
    def content(self):
        if self.req_counter == 0:
            url = reverse('entity_configuration')
            res = self.client.get(url, data={'sub': ta_conf_data['sub']})
        elif self.req_counter == 1:
            rp = FederationEntityConfiguration.objects.get(sub=rp_onboarding_data['sub'])
            res = DummyContent(rp.entity_configuration_as_jws)
        elif self.req_counter == 2:
            sa = FederationEntityConfiguration.objects.get(sub=intermediary_conf['sub'])
            res = DummyContent(sa.entity_configuration_as_jws)
        elif self.req_counter == 3:
            url = reverse('oidcfed_fetch')
            res = self.client.get(url,
                data={'sub': rp_onboarding_data['sub'], 'iss': intermediary_conf['sub']}
            )
        elif self.req_counter == 4:
            url = reverse('oidcfed_fetch')
            res = self.client.get(url, data={'sub': intermediary_conf['sub']})
        elif self.req_counter == 5:
            url = reverse('entity_configuration')
            res = self.client.get(url, data={'sub': ta_conf_data['sub']})
        
        elif self.req_counter > 5:
            raise NotImplementedError(
                "The mocked resposes seems to be not aligned with the correct flow"
            )

        if res.status_code != 200:
            raise HttpError(
                f"Something went wrong with Http Request: {res.__dict__}"
            )
        
        self.req_counter += 1
        logger.info(
            # json.dumps(
                unpad_jwt_payload(res.content.decode()),
                # indent=2)
            )
        return res.content
