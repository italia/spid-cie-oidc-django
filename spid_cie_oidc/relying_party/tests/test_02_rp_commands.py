from django.conf import settings
from django.core.management import call_command
from django.test import TestCase
from io import StringIO


class OidcRPCliTests(TestCase):
    def setUp(self):
        # create a FederationEntityConfiguration SP
        pass

    
    def test_fetch_openid_providers(self):
        overrides = dict(
            OIDCFED_IDENTITY_PROVIDERS = ,
            OIDCFED_REQUIRED_TRUST_MARKS = 
        )
        
        with self.settings(**overrides):
            pass
            #out = self.call_command('fetch_openid_providers', '--start')
            #self.assertEqual(out.splitlines()[0], "test arbitrary command")
    
