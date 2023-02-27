import json

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import (
    Client, 
    RequestFactory, 
    TestCase, 
    override_settings
)
from django.urls import reverse
from spid_cie_oidc.entity.tests.rp_metadata_settings import rp_conf
from spid_cie_oidc.entity.views import resolve_entity_statement
from spid_cie_oidc.entity.models import (
    FederationEntityConfiguration,
    FetchedEntityStatement, 
    TrustChain,
    StaffToken
)
from spid_cie_oidc.entity.tests.settings import ta_conf_data
from spid_cie_oidc.entity.utils import (
    datetime_from_timestamp, 
    exp_from_now,
    iat_now
)


def create_tc():
    

    TA_FES = FetchedEntityStatement.objects.create(
        sub="http://testserver/",
        iss="http://testserver/",
        exp=datetime_from_timestamp(exp_from_now(33)),
        iat=datetime_from_timestamp(iat_now()),
    )
    return TrustChain.objects.create(
        sub="http://rp-test.it/oidc/rp/",
        exp=datetime_from_timestamp(exp_from_now(33)),
        jwks = [],
        metadata=[],
        status="valid",
        trust_anchor=TA_FES,
        is_active=True,
    )

class ResolveEntityStatementTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create(
            username="test",
            first_name="test",
            last_name="test",
            email="test@test.it",
            is_staff = True
        )
        self.user.set_password("test")
        self.user.save()
        StaffToken.objects.create(
            user = self.user,
            token = "secret-token",
            is_active = True
        )
        self.ta_conf = FederationEntityConfiguration.objects.create(**ta_conf_data)
        self.sub_conf = FederationEntityConfiguration.objects.create(**rp_conf)
        self.ta_fes = FetchedEntityStatement.objects.create(
            sub=ta_conf_data["sub"],
            iss=ta_conf_data["sub"],
            exp=datetime_from_timestamp(exp_from_now(33)),
            iat=datetime_from_timestamp(iat_now()),
        )



    @override_settings(HTTP_CLIENT_SYNC=True)
    def test_resolve_entity_statement(self):
        client = Client()
        url = reverse("oidcfed_resolve")
        client.login(username="test", password="test")
        data = {"sub" : rp_conf["sub"], "anchor" : ta_conf_data["sub"]}
        request = self.factory.get(url, data, **{'HTTP_AUTHORIZATION': "secret-token"})
        self.patcher = patch(
            "spid_cie_oidc.entity.trust_chain_operations.get_or_create_trust_chain", 
            return_value = create_tc()
        )
        self.patcher.start()
        res = resolve_entity_statement(request, format='json')
        self.patcher.stop()
        _json = json.loads(res.content.decode())
        self.assertTrue(_json.get("iss") == ta_conf_data["sub"])
        self.assertTrue(_json.get("sub") == rp_conf["sub"])

        self.assertTrue("trust_chain" in _json)
        self.assertTrue("metadata" in _json)
