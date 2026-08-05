from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from spid_cie_oidc.authority.tests.settings import RP_METADATA_JWK1
from spid_cie_oidc.entity.jwtse import create_jws
from spid_cie_oidc.entity.models import FederationEntityConfiguration, FetchedEntityStatement
from spid_cie_oidc.entity.tests.settings import TA_SUB
from spid_cie_oidc.entity.utils import datetime_from_timestamp, exp_from_now, iat_now
from spid_cie_oidc.provider.tests.settings import op_conf
from spid_cie_oidc.relying_party.utils import random_string

# An attacker-chosen subject that is NOT part of the federation (no trust chain
# exists for it in the database).
ATTACKER_SUB = "https://attacker.example/oidc/rp/"


class AuthzRequestSSRFTest(TestCase):
    """
    An unauthenticated authorization request must not be able to make the OP
    fetch an arbitrary URL: on-the-fly trust chain discovery is only allowed for
    subjects already known inside the federation (CWE-918).
    """

    def setUp(self):
        self.user = get_user_model().objects.create(username="test", email="test@test.it")
        self.user.set_password("test")
        self.user.save()
        self.op_conf = FederationEntityConfiguration.objects.create(**op_conf)
        self.ta_fes = FetchedEntityStatement.objects.create(
            sub=TA_SUB,
            iss=TA_SUB,
            exp=datetime_from_timestamp(exp_from_now(33)),
            iat=datetime_from_timestamp(iat_now()),
        )
        self.payload = {
            "client_id": ATTACKER_SUB,
            "sub": ATTACKER_SUB,
            "iss": ATTACKER_SUB,
            "response_type": "code",
            "scope": ["openid"],
            "nonce": random_string(),
            "prompt": "consent login",
            "redirect_uri": f"{ATTACKER_SUB}callback/",
            "acr_values": ["https://www.spid.gov.it/SpidL2"],
            "state": random_string(),
            "aud": ["https://op.spid.agid.gov.it/auth"],
            "iat": iat_now(),
            "exp": exp_from_now(),
            "jti": random_string(),
        }

    @override_settings(OIDCFED_TRUST_ANCHORS=[TA_SUB])
    def test_unknown_subject_does_not_trigger_outbound_fetch(self):
        jws = create_jws(self.payload, RP_METADATA_JWK1)
        client = Client()
        url = reverse("oidc_provider_authnrequest")

        with patch(
            "spid_cie_oidc.provider.views.get_or_create_trust_chain",
            new=MagicMock(name="get_or_create_trust_chain"),
        ) as mocked_discovery:
            res = client.get(url, {"request": jws})

        # The server refused the request instead of building a trust chain, and
        # crucially it did NOT perform any outbound discovery fetch.
        mocked_discovery.assert_not_called()
        self.assertEqual(res.status_code, 302)
        self.assertIn("error", res.url)
