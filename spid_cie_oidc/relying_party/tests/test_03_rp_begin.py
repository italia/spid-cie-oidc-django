import urllib

from copy import deepcopy
from unittest.mock import patch

from django.http import HttpRequest
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from spid_cie_oidc.authority.tests.settings import rp_conf
from spid_cie_oidc.entity.models import (
    FederationEntityConfiguration,
    FetchedEntityStatement,
    TrustChain,
)
from spid_cie_oidc.entity.jwtse import unpad_jwt_payload
from spid_cie_oidc.entity.tests.settings import TA_SUB
from spid_cie_oidc.entity.utils import datetime_from_timestamp, exp_from_now, iat_now
from spid_cie_oidc.provider.tests.settings import op_conf

def create_tc():
    NOW = datetime_from_timestamp(iat_now())
    EXP = datetime_from_timestamp(exp_from_now(33))
    ta_fes = FetchedEntityStatement.objects.create(
        sub=TA_SUB,
        iss=TA_SUB,
        exp=EXP,
        iat=NOW,
    )
    return TrustChain.objects.create(
        sub=op_conf["sub"],
        exp=EXP,
        jwks = [],
        status="valid",
        trust_anchor=ta_fes,
        is_active=True,
    )

def create_tc_metadata_no_correct():
    NOW = datetime_from_timestamp(iat_now())
    EXP = datetime_from_timestamp(exp_from_now(33))
    ta_fes = FetchedEntityStatement.objects.create(
        sub=TA_SUB,
        iss=TA_SUB,
        exp=EXP,
        iat=NOW,
    )
    local_op_conf = deepcopy(op_conf)
    metadata = local_op_conf["metadata"]
    metadata["openid_provider"]["jwks"] = {"keys": []}
    return TrustChain.objects.create(
        sub=op_conf["sub"],
        exp=EXP,
        status="valid",
        jwks = [],
        metadata=metadata,
        trust_anchor=ta_fes,
        is_active=True,
    )

class RPBeginTest(TestCase):

    def setUp(self):
        self.req = HttpRequest()
        NOW = datetime_from_timestamp(iat_now())
        EXP = datetime_from_timestamp(exp_from_now(33))
        self.rp_conf = FederationEntityConfiguration.objects.create(**rp_conf)
        self.ta_fes = FetchedEntityStatement.objects.create(
            sub=TA_SUB,
            iss=TA_SUB,
            exp=EXP,
            iat=NOW,
        ) 
        metadata = deepcopy(op_conf["metadata"])
        self.trust_chain = TrustChain.objects.create(
            sub=op_conf["sub"],
            exp=EXP,
            jwks = [],
            metadata=metadata,
            status="valid",
            trust_anchor=self.ta_fes,
            is_active=True,
        )
   

    @override_settings(OIDCFED_DEFAULT_TRUST_ANCHOR=TA_SUB, OIDCFED_TRUST_ANCHORS=[TA_SUB])
    def test_rp_begin(self):
        client = Client()
        url = reverse("spid_cie_rp_begin")
        res = client.get(url, {"provider": op_conf["sub"], "trust_anchor": TA_SUB})
        self.assertTrue(res.status_code == 302)

    @override_settings(OIDCFED_DEFAULT_TRUST_ANCHOR=TA_SUB, OIDCFED_TRUST_ANCHORS=[TA_SUB])
    @patch("spid_cie_oidc.relying_party.views.rp_begin.SpidCieOidcRpBeginView.get_oidc_op", return_value=None)
    def test_rp_begin_no_tc(self, mocked):
        client = Client()
        url = reverse("spid_cie_rp_begin")
        res = client.get(url, {"provider": op_conf["sub"], "trust_anchor": TA_SUB})
        self.assertTrue("request rejected" in res.content.decode())

    def test_no_request(self):
        client = Client()
        url = reverse("spid_cie_rp_begin")
        res = client.get(url, {"request": {}})
        self.assertTrue(res.status_code == 404)
        self.assertTrue("request rejected" in res.content.decode())
        self.assertTrue("Missing provider url" in res.content.decode())

    # I changed the code to get a smarter solution
    @override_settings(OIDCFED_DEFAULT_TRUST_ANCHOR=TA_SUB)
    def test_no_unallowed_tc(self):
        client = Client()
        url = reverse("spid_cie_rp_begin")
        res = client.get(url, {"provider": "provider"})
        self.assertTrue(res.status_code == 404)
        self.assertTrue("request rejected" in res.content.decode())
        self.assertTrue("Unallowed Trust Anchor" in res.content.decode())

    @override_settings(OIDCFED_DEFAULT_TRUST_ANCHOR=TA_SUB, OIDCFED_TRUST_ANCHORS=[TA_SUB])
    def test_no_rp_entity_conf(self):
        FederationEntityConfiguration.objects.all().delete()
        client = Client()
        url = reverse("spid_cie_rp_begin")
        res = client.get(url, {"provider": op_conf["sub"], "trust_anchor": TA_SUB})
        self.assertTrue(res.status_code == 404)
        self.assertTrue("request rejected" in res.content.decode())
        self.assertTrue("Missing configuration" in res.content.decode())

    @override_settings(OIDCFED_DEFAULT_TRUST_ANCHOR=TA_SUB, OIDCFED_TRUST_ANCHORS=[TA_SUB])
    def test_invalid_provider_metadata(self):
        metadata = deepcopy(op_conf["metadata"])
        metadata["openid_provider"].pop("jwks")
        self.trust_chain.metadata = metadata
        self.trust_chain.save()
        client = Client()
        url = reverse("spid_cie_rp_begin")
        res = client.get(url, {"provider": op_conf["sub"], "trust_anchor": TA_SUB})
        self.assertTrue(res.status_code == 404)
        self.assertTrue("request rejected" in res.content.decode())
        self.assertTrue("Invalid provider Metadata" in res.content.decode())

    @override_settings(OIDCFED_DEFAULT_TRUST_ANCHOR=TA_SUB, OIDCFED_TRUST_ANCHORS=[TA_SUB])
    def test_tc_no_active(self):
        self.trust_chain.is_active = False
        self.trust_chain.save()
        client = Client()
        url = reverse("spid_cie_rp_begin")
        res = client.get(url, {"provider": op_conf["sub"], "trust_anchor": TA_SUB})
        self.assertTrue(res.status_code == 404)
        self.assertTrue("request rejected" in res.content.decode())
        self.assertTrue("found but DISABLED at" in res.content.decode())

    @override_settings(OIDCFED_DEFAULT_TRUST_ANCHOR=TA_SUB, OIDCFED_TRUST_ANCHORS=[TA_SUB])
    def test_failed_to_get_jwks(self):
        metadata = deepcopy(op_conf["metadata"])
        metadata['openid_provider'].pop("jwks")
        metadata["jwks_uri"] = "jwks_uri"
        self.trust_chain.metadata = metadata
        self.trust_chain.save()
        client = Client()
        url = reverse("spid_cie_rp_begin")
        res = client.get(url, {"provider": op_conf["sub"], "trust_anchor": TA_SUB})
        
        self.assertTrue(res.status_code == 404)
        self.assertTrue("request rejected" in res.content.decode())

    def test_rp_begin_tc_no_metadata(self):
        client = Client()
        url = reverse("spid_cie_rp_begin")
        self.patcher = patch(
            "spid_cie_oidc.relying_party.views.rp_begin.SpidCieOidcRpBeginView.get_oidc_op", 
            return_value = create_tc()
        )
        self.patcher.start()
        res = client.get(url, {"provider": op_conf["sub"], "trust_anchor": TA_SUB})
        self.assertTrue("request rejected" in res.content.decode())
        self.patcher.stop()
    
    @override_settings(OIDCFED_DEFAULT_TRUST_ANCHOR=TA_SUB, OIDCFED_TRUST_ANCHORS=[TA_SUB])
    def test_rp_begin_tc_no_redirect_uri(self):
        red_url = "http://rp-test.it/oidc/rp/callback-test/"
        FederationEntityConfiguration.objects.all().delete()
        local_rp_conf = deepcopy(rp_conf)
        local_rp_conf["metadata"]["openid_relying_party"]["redirect_uris"] = [red_url],
        self.rp_conf = FederationEntityConfiguration.objects.create(**local_rp_conf)        
        client = Client()
        url = reverse("spid_cie_rp_begin")
        TrustChain.objects.all()
        res = client.get(
            url, 
            {
                "provider": op_conf["sub"], 
                "trust_anchor": TA_SUB,
                "redirect_uri": "http://rp-test.it/oidc/rp/callback"
            }
        )
        req = urllib.parse.parse_qs(res.url)['request'][0]
        req_data = unpad_jwt_payload(req)
        self.assertTrue(red_url in req_data['redirect_uri'])
