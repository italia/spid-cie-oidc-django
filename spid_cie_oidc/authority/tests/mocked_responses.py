from django.test import Client
from django.urls import reverse

from spid_cie_oidc.entity.models import FederationEntityConfiguration
from spid_cie_oidc.entity.jwtse import unpad_jwt_payload, create_jws
from spid_cie_oidc.entity.exceptions import HttpError
from spid_cie_oidc.entity.tests.settings import ta_conf_data

from .settings import rp_onboarding_data, intermediary_conf, rp_conf

import copy
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
        self.result = None

    def result_as_it_is(self):
        logger.info(f"Response #{self.req_counter}: {self.result.content.decode()}")
        self.req_counter += 1
        return self.result.content

    def result_as_jws(self):
        logger.info(
            f"Response #{self.req_counter}: "
            f"{unpad_jwt_payload(self.result.content.decode())}"
        )
        self.req_counter += 1
        return self.result.content

    def trust_anchor_ec(self):
        url = reverse("entity_configuration")
        res = self.client.get(url, data={"sub": ta_conf_data["sub"]})
        return res

    def rp_ec(self):
        rp = FederationEntityConfiguration.objects.get(sub=rp_onboarding_data["sub"])
        res = DummyContent(rp.entity_configuration_as_jws)
        return res

    def fetch_rp_from_ta(self):
        url = reverse("oidcfed_fetch")
        res = self.client.get(url, data={"sub": rp_onboarding_data["sub"]})
        return res


class EntityResponseNoIntermediate(EntityResponse):
    @property
    def content(self):
        if self.req_counter == 0:
            self.result = self.trust_anchor_ec()
        elif self.req_counter == 1:
            self.result = self.rp_ec()
        elif self.req_counter == 2:
            self.result = self.fetch_rp_from_ta()
        elif self.req_counter > 2:
            raise NotImplementedError(
                "The mocked resposes seems to be not aligned with the correct flow"
            )

        return self.result_as_jws()

class EntityResponseNoIntermediateSignedJwksUri(EntityResponse):
    @property
    def content(self):
        if self.req_counter == 0:
            self.result = self.trust_anchor_ec()
        elif self.req_counter == 1:
            self.result = self.rp_ec()
        elif self.req_counter == 2:
            self.result = self.fetch_rp_from_ta()
        elif self.req_counter == 3:
            metadata = copy.deepcopy(rp_conf['metadata']['openid_relying_party'])
            _jwks = metadata.pop('jwks')
            fed_jwks = rp_conf['jwks_fed'][0]
            self.result = create_jws(_jwks, fed_jwks)
            return self.result.encode()
        elif self.req_counter > 3:
            raise NotImplementedError(
                "The mocked resposes seems to be not aligned with the correct flow"
            )

        return self.result_as_jws()


class EntityResponseWithIntermediate(EntityResponse):
    @property
    def content(self):
        if self.req_counter == 0:
            self.result = self.trust_anchor_ec()
        elif self.req_counter == 1:
            self.result = self.rp_ec()
        elif self.req_counter == 2:
            sa = FederationEntityConfiguration.objects.get(sub=intermediary_conf["sub"])
            self.result = DummyContent(sa.entity_configuration_as_jws)
        elif self.req_counter == 3:
            url = reverse("oidcfed_fetch")
            self.result = self.client.get(
                url,
                data={
                    "sub": rp_onboarding_data["sub"],
                    "iss": intermediary_conf["sub"],
                },
            )
        elif self.req_counter == 4:
            url = reverse("oidcfed_fetch")
            self.result = self.client.get(url, data={"sub": intermediary_conf["sub"]})
        elif self.req_counter == 5:
            url = reverse("entity_configuration")
            self.result = self.client.get(url, data={"sub": ta_conf_data["sub"]})
        elif self.req_counter > 5:
            raise NotImplementedError(
                "The mocked resposes seems to be not aligned with the correct flow"
            )

        if self.result.status_code != 200:
            raise HttpError(f"Something went wrong with Http Request: {res.__dict__}")

        logger.info("-------------------------------------------------")
        logger.info("")
        return self.result_as_jws()


class EntityResponseWithIntermediateManyHints(EntityResponse):
    @property
    def content(self):
        if self.req_counter == 0:
            self.result = self.trust_anchor_ec()
        elif self.req_counter == 1:
            self.result = self.rp_ec()
        elif self.req_counter == 2:
            sa = FederationEntityConfiguration.objects.get(sub=intermediary_conf["sub"])
            self.result = DummyContent(sa.entity_configuration_as_jws)
        elif self.req_counter == 3:
            self.result = DummyContent("crap")

        elif self.req_counter == 4:
            url = reverse("oidcfed_fetch")
            self.result = self.client.get(
                url,
                data={
                    "sub": rp_onboarding_data["sub"],
                    "iss": intermediary_conf["sub"],
                },
            )
        elif self.req_counter == 5:
            url = reverse("oidcfed_fetch")
            self.result = self.client.get(url, data={"sub": intermediary_conf["sub"]})
        elif self.req_counter == 6:
            url = reverse("entity_configuration")
            self.result = self.client.get(url, data={"sub": ta_conf_data["sub"]})
        elif self.req_counter > 6:
            raise NotImplementedError(
                "The mocked resposes seems to be not aligned with the correct flow"
            )
        if self.result.status_code != 200:
            raise HttpError(f"Something went wrong with Http Request: {res.__dict__}")

        try:
            return self.result_as_jws()
        except:
            return self.result_as_it_is()
