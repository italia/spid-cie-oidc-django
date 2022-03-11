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
from spid_cie_oidc.entity.tests.settings import TA_SUB
from spid_cie_oidc.entity.utils import datetime_from_timestamp, exp_from_now, iat_now
from spid_cie_oidc.provider.tests.settings import op_conf


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
        self.trust_chain = TrustChain.objects.create(
            sub=op_conf["sub"],
            type="openid_relying_party",
            exp=EXP,
            metadata=op_conf["metadata"]["openid_provider"],
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
    @patch("spid_cie_oidc.relying_party.views.SpidCieOidcRpBeginView.get_oidc_op", return_value=None)
    def test_rp_begin_no_tc(self, mocked):
        client = Client()
        url = reverse("spid_cie_rp_begin")
        res = client.get(url, {"provider": op_conf["sub"], "trust_anchor": TA_SUB})
        self.assertTrue("request rejected" in res.content.decode())

    def test_no_request(self):
        client = Client()
        url = reverse("spid_cie_rp_begin")
        res = client.get(url, {"request": {}})
        self.assertTrue(res.status_code == 200)
        self.assertTrue("request rejected" in res.content.decode())
        self.assertTrue("Missing provider url" in res.content.decode())

    # I changed the code to get a smarter solution
    @override_settings(OIDCFED_DEFAULT_TRUST_ANCHOR=TA_SUB)
    def test_no_unallowed_tc(self):
        client = Client()
        url = reverse("spid_cie_rp_begin")
        res = client.get(url, {"provider": "provider"})
        self.assertTrue(res.status_code == 200)
        self.assertTrue("request rejected" in res.content.decode())
        self.assertTrue("Unallowed Trust Anchor" in res.content.decode())

    @override_settings(OIDCFED_DEFAULT_TRUST_ANCHOR=TA_SUB, OIDCFED_TRUST_ANCHORS=[TA_SUB])
    def test_no_rp_entity_conf(self):
        FederationEntityConfiguration.objects.all().delete()
        client = Client()
        url = reverse("spid_cie_rp_begin")
        res = client.get(url, {"provider": op_conf["sub"], "trust_anchor": TA_SUB})
        self.assertTrue(res.status_code == 200)
        self.assertTrue("request rejected" in res.content.decode())
        self.assertTrue("Missing configuration" in res.content.decode())

    @override_settings(OIDCFED_DEFAULT_TRUST_ANCHOR=TA_SUB, OIDCFED_TRUST_ANCHORS=[TA_SUB])
    def test_invalid_provider_metadata(self):
        metadata = deepcopy(op_conf["metadata"]["openid_provider"])
        self.trust_chain.metadata = metadata.pop("jwks")
        self.trust_chain.save()
        client = Client()
        url = reverse("spid_cie_rp_begin")
        res = client.get(url, {"provider": op_conf["sub"], "trust_anchor": TA_SUB})
        self.assertTrue(res.status_code == 200)
        self.assertTrue("request rejected" in res.content.decode())
        self.assertTrue("Invalid provider Metadata" in res.content.decode())

    @override_settings(OIDCFED_DEFAULT_TRUST_ANCHOR=TA_SUB, OIDCFED_TRUST_ANCHORS=[TA_SUB])
    def test_tc_no_active(self):
        self.trust_chain.is_active = False
        self.trust_chain.save()
        client = Client()
        url = reverse("spid_cie_rp_begin")
        res = client.get(url, {"provider": op_conf["sub"], "trust_anchor": TA_SUB})
        self.assertTrue(res.status_code == 200)
        self.assertTrue("request rejected" in res.content.decode())
        self.assertTrue("found but DISABLED at" in res.content.decode())

    @override_settings(OIDCFED_DEFAULT_TRUST_ANCHOR=TA_SUB, OIDCFED_TRUST_ANCHORS=[TA_SUB])
    def test_failed_to_get_jwks(self):
        metadata = deepcopy(op_conf["metadata"]["openid_provider"])
        metadata.pop("jwks")
        metadata["jwks_uri"] = "jwks_uri"
        self.trust_chain.metadata = metadata
        self.trust_chain.save()
        client = Client()
        url = reverse("spid_cie_rp_begin")
        res = client.get(url, {"provider": op_conf["sub"], "trust_anchor": TA_SUB})
        self.assertTrue(res.status_code == 200)
        self.assertTrue("request rejected" in res.content.decode())
        self.assertTrue("Failed to get jwks from " in res.content.decode())
