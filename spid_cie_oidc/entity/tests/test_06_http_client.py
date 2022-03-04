

import asyncio

from django.test import TestCase
from spid_cie_oidc.entity.http_client import http_get


class HttpClient(TestCase):

    def test_http_client(self):
        url = "https://icanhazip.com/"
        get = http_get([url], {})
        value = asyncio.run(get)
        self.assertTrue("93.71.202.64" in str(value))

