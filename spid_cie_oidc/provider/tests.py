
from django.http import HttpRequest
from django.test import TestCase
from spid_cie_oidc.authority.tests.settings import *
from spid_cie_oidc.entity.jwtse import create_jws
from spid_cie_oidc.entity.models import FetchedEntityStatement, TrustChain
from spid_cie_oidc.entity.tests.settings import *
from spid_cie_oidc.provider.settings import *
from spid_cie_oidc.provider.views import authn_request


class AuthnRequestTest(TestCase):

    def setUp(self):
        self.req = HttpRequest()


    def test_auth_request(self):
        jws=create_jws(PAYLOAD,JWK)
        self.req.GET = {'request':jws}
        fes = FetchedEntityStatement.objects.create(
            sub = "http://rp-test/oidc/rp",
            iss = "http://rp-test/oidc/rp",
            #TODO: iat e exp dinamiche
            exp = "2022-12-28 23:00",
            iat = "2022-02-26 15:00",
            )
        
        TrustChain.objects.create(
            sub = 'http://rp-test/oidc/rp',
            type = "openid_relying_party",
            #TODO: exp dinamiche
            exp = "2022-12-28 23:00",
            metadata = METADATA,
            status = 'valid',
            trust_anchor = fes,
            is_active = True
            )

        # please reDO with a django Client as the request were produced by a browser
        # res = authn_request(self.req)
        # self.assertTrue(res.status_code == 200)
        # self.assertIn("username", res.content.decode())
        # self.assertIn("password", res.content.decode())


