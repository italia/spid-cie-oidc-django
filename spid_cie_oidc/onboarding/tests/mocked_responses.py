from unittest import result
from spid_cie_oidc.authority.tests.mocked_responses import EntityResponse
from django.test import Client
from django.urls import reverse

from spid_cie_oidc.entity.models import FederationEntityConfiguration
from spid_cie_oidc.authority.tests.settings import rp_onboarding_data
from spid_cie_oidc.entity.tests.settings import ta_conf_data
import logging

logger = logging.getLogger(__name__)

class OnboardingRegistrationResponse():

    def __init__(self):
        self.status_code = 200
        self.req_counter = 0
        self.client = Client()
        self.result = None

    @property
    def content(self):
        self.req_counter += 1
