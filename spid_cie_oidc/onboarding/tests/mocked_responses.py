from django.test import Client

import logging

logger = logging.getLogger(__name__)


class OnboardingRegistrationResponse:
    def __init__(self):
        self.status_code = 200
        self.req_counter = 0
        self.client = Client()
        self.result = None

    @property
    def content(self):
        self.req_counter += 1
