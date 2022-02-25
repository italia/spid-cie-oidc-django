from django.test import TestCase, Client, override_settings
from django.urls import reverse

from spid_cie_oidc.entity.exceptions import InvalidRequiredTrustMark
from spid_cie_oidc.entity.jwtse import verify_jws
from spid_cie_oidc.entity.models import *
from spid_cie_oidc.entity.trust_chain import trust_chain_builder
from spid_cie_oidc.entity.statements import (
    EntityConfiguration,
    get_entity_configurations,
)
from spid_cie_oidc.entity.tests.settings import *

from spid_cie_oidc.authority.models import *
from spid_cie_oidc.authority.tests.mocked_responses import *
from spid_cie_oidc.authority.tests.settings import *


from unittest.mock import patch

import datetime


class TATest(TestCase):
    def setUp(self):
        self.ta_conf = FederationEntityConfiguration.objects.create(**ta_conf_data)
        self.rp_conf = FederationEntityConfiguration.objects.create(**rp_conf)

        self.rp_profile = FederationEntityProfile.objects.create(**RP_PROFILE)
        self.rp = FederationDescendant.objects.create(**rp_onboarding_data)

        self.rp_jwk = PublicJwk.objects.create(
            jwk=self.rp_conf.public_jwks[0], kid=self.rp_conf.public_jwks[0]["kid"]
        )
        FederationDescendantJwk.objects.create(descendant=self.rp, jwk=self.rp_jwk)
        FederationEntityAssignedProfile.objects.create(
            descendant=self.rp, profile=self.rp_profile, issuer=self.ta_conf
        )

    def test_fetch_endpoint(self):
        url = reverse("oidcfed_fetch")
        c = Client()
        res = c.get(url, data={"sub": self.rp.sub})
        data = verify_jws(res.content.decode(), self.ta_conf.jwks[0])
        self.assertTrue(data["jwks"])

    def test_list_endpoint(self):
        url = reverse("oidcfed_list")
        c = Client()
        res = c.get(url, data={"is_leaf": True})
        self.assertTrue(res.json()[0] == self.rp.sub)
        self.assertEqual(res.status_code, 200)

        res = c.get(url, data={"is_leaf": False})
        self.assertFalse(res.json())
        self.assertEqual(res.status_code, 200)

        res = c.get(url, data={})
        self.assertTrue(res.json())
        self.assertEqual(res.status_code, 200)

    @override_settings(HTTP_CLIENT_SYNC=True)
    @patch("requests.get", return_value=EntityResponseNoIntermediate())
    def test_trust_chain_valid_no_intermediaries(self, mocked):

        self.ta_conf.constraints = {"max_path_length": 0}
        self.ta_conf.save()

        jwt = get_entity_configurations(self.ta_conf.sub)
        trust_anchor_ec = EntityConfiguration(jwt[0])

        trust_chain = trust_chain_builder(
            subject=rp_onboarding_data["sub"],
            trust_anchor=trust_anchor_ec,
            metadata_type="openid_relying_party",
        )
        self.assertTrue(trust_chain)
        self.assertTrue(trust_chain.final_metadata)

        for i in trust_chain.tree_of_trust.values():
            for ec in i:
                self.assertTrue(ec.is_valid)

        for ec in trust_chain.trust_path:
            self.assertTrue(ec.is_valid)

        self.assertTrue(len(trust_chain.trust_path) == 2)
        self.assertTrue((len(trust_chain.trust_path) - 2) == trust_chain.max_path_len)

        self.assertTrue(isinstance(trust_chain.exp, int))
        self.assertTrue(isinstance(trust_chain.exp_datetime, datetime.datetime))

    def _create_federation_with_intermediary(self) -> EntityConfiguration:
        jwt = get_entity_configurations(self.ta_conf.sub)
        trust_anchor_ec = EntityConfiguration(jwt[0])

        self.intermediate = FederationEntityConfiguration.objects.create(
            **intermediary_conf
        )
        self.intermediate_jwk = PublicJwk.objects.create(
            jwk=self.intermediate.public_jwks[0],
            kid=self.intermediate.public_jwks[0]["kid"],
        )
        self.intermediate_desc = FederationDescendant.objects.create(
            **intermediary_onboarding_data
        )
        FederationDescendantJwk.objects.create(
            descendant=self.intermediate_desc, jwk=self.intermediate_jwk
        )
        FederationEntityAssignedProfile.objects.create(
            descendant=self.rp, profile=self.rp_profile, issuer=self.intermediate
        )
        self.rp_conf.authority_hints = [intermediary_conf["sub"]]
        self.rp_conf.save()
        return trust_anchor_ec

    @override_settings(HTTP_CLIENT_SYNC=True)
    @patch("requests.get", return_value=EntityResponseWithIntermediate())
    def test_trust_chain_valid_with_intermediary(self, mocked):

        trust_anchor_ec = self._create_federation_with_intermediary()

        trust_chain = trust_chain_builder(
            subject=self.rp.sub,
            trust_anchor=trust_anchor_ec,
            metadata_type="openid_relying_party"
        )
        
        self.assertTrue(trust_chain)
        self.assertTrue(trust_chain.final_metadata)

        for i in trust_chain.tree_of_trust.values():
            for ec in i:
                self.assertTrue(ec.is_valid)

        for ec in trust_chain.trust_path:
            self.assertTrue(ec.is_valid)
        
        self.assertTrue(len(trust_chain.trust_path) == 3)
        self.assertTrue(
            (len(trust_chain.trust_path) - 2) == trust_chain.max_path_len
        )

    @override_settings(HTTP_CLIENT_SYNC=True)
    @patch("requests.get", return_value=EntityResponseWithIntermediateManyHints())
    def test_trust_chain_valid_with_intermediaries_many_authhints(self, mocked):
        
        trust_anchor_ec = self._create_federation_with_intermediary()

        self.rp_conf.authority_hints = [
            'http://intermediary-test', "http://that-faulty"
        ]
        self.rp_conf.save()
        
        trust_chain = trust_chain_builder(
            subject=self.rp.sub,
            trust_anchor=trust_anchor_ec,
            metadata_type="openid_relying_party",
        )

        for ec in trust_chain.trust_path:
            self.assertTrue(ec.is_valid)

        self.assertTrue(len(trust_chain.trust_path) == 3)
        self.assertTrue(
            (len(trust_chain.trust_path) - 2) == trust_chain.max_path_len
        )

    @override_settings(HTTP_CLIENT_SYNC=True)
    @patch("requests.get", return_value=EntityResponseWithIntermediate())
    def test_trust_chain_valid_with_intermediaries_and_trust_mark_filter(self, mocked):
        
        trust_anchor_ec = self._create_federation_with_intermediary()

        # the RP exposes a trust marks in its entity configuration
        self.rp_conf.trust_marks = [
            FederationEntityAssignedProfile.objects.filter(
                descendant=self.rp
            ).first().trust_mark
        ]
        self.rp_conf.save()
        
        trust_chain = trust_chain_builder(
            subject=self.rp.sub,
            trust_anchor=trust_anchor_ec,
            metadata_type="openid_relying_party",
            required_trust_marks = [
                'https://www.spid.gov.it/certification/rp'
            ]
        )

        for ec in trust_chain.trust_path:
            self.assertTrue(ec.is_valid)

        self.assertTrue(len(trust_chain.trust_path) == 3)
        self.assertTrue(
            (len(trust_chain.trust_path) - 2) == trust_chain.max_path_len
        )

    @override_settings(HTTP_CLIENT_SYNC=True)
    @patch("requests.get", return_value=EntityResponseWithIntermediate())
    def test_trust_chain_with_missing_trust_mark(self, mocked):
        
        trust_anchor_ec = self._create_federation_with_intermediary()

        with self.assertRaises(InvalidRequiredTrustMark):
            trust_chain = trust_chain_builder(
                subject=self.rp.sub,
                trust_anchor=trust_anchor_ec,
                metadata_type="openid_relying_party",
                required_trust_marks = [
                    'https://www.spid.gov.it/certification/rp'
                ]
            )
    
