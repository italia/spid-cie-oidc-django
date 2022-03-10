

import os
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase, override_settings
from spid_cie_oidc.authority.tests.settings import RP_CONF, RP_METADATA_JWK1
from spid_cie_oidc.entity.jwtse import create_jws
from spid_cie_oidc.entity.models import FederationEntityConfiguration, FetchedEntityStatement
from spid_cie_oidc.entity.tests.settings import ta_conf_data

from spid_cie_oidc.entity.tests.settings import TA_SUB
from spid_cie_oidc.entity.utils import (
    datetime_from_timestamp, 
    exp_from_now,
    iat_now
)
JWS = create_jws(RP_CONF, RP_METADATA_JWK1)

class FetchProviderTest(TestCase):

    def setUp(self):

        self.ta_fes = FetchedEntityStatement.objects.create(
            sub=TA_SUB,
            iss=TA_SUB,
            exp=datetime_from_timestamp(exp_from_now(33)),
            iat=datetime_from_timestamp(iat_now()),
        )


    def call_command(self, cmd_name:str, *args, **kwargs):
        out = StringIO()
        err = StringIO()
        call_command(
            cmd_name,
            *args,
            stdout=out,
            stderr=err,
            **kwargs,
        )
        return out.getvalue()
    
    @patch("spid_cie_oidc.entity.statements.get_entity_configurations", return_value = [JWS])
    @override_settings(OIDCFED_IDENTITY_PROVIDERS = {"http://127.0.0.1:8000/oidc/op/" :"http://testserver/"})
    def test_fetch_provider(self, mocked):
        out = self.call_command('fetch_openid_providers', '--start')
        self.assertEqual(out.splitlines()[0], "Found")


