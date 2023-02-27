from django.test import TestCase, Client, override_settings
from django.urls import reverse

from spid_cie_oidc.entity.exceptions import InvalidRequiredTrustMark
from spid_cie_oidc.entity.jwtse import verify_jws
from spid_cie_oidc.entity.models import *

from spid_cie_oidc.entity.trust_chain_operations import (
    dumps_statements_from_trust_chain_to_db,
    get_or_create_trust_chain,
    trust_chain_builder,
)
from spid_cie_oidc.entity.statements import (
    EntityConfiguration,
    get_entity_configurations,
    TrustMark,
)
from spid_cie_oidc.entity.utils import get_jwks
from spid_cie_oidc.entity.tests.settings import *

from spid_cie_oidc.authority.models import *
from spid_cie_oidc.authority.tests.mocked_responses import *
from spid_cie_oidc.authority.tests.settings import *


from unittest.mock import patch

import copy
import datetime


class TrustChainTest(TestCase):
    def setUp(self):
        self.ta_conf = FederationEntityConfiguration.objects.create(**ta_conf_data)
        self.rp_conf = FederationEntityConfiguration.objects.create(**rp_conf)

        self.rp_profile = FederationEntityProfile.objects.create(**RP_PROFILE)
        self.rp = FederationDescendant.objects.create(**rp_onboarding_data)
 
        self.rp_assigned_profile = FederationEntityAssignedProfile.objects.create(
            descendant=self.rp, profile=self.rp_profile, issuer=self.ta_conf
        )

    def test_fetch_endpoint(self):
        self.rp_profile.__str__()
        self.rp_profile.trust_mark_template_as_json
        url = reverse("oidcfed_fetch")
        c = Client()
        res = c.get(url, data={"sub": self.rp.sub})
        data = verify_jws(res.content.decode(), self.ta_conf.jwks_fed[0])
        self.assertTrue(data["jwks"])

    def test_list_endpoint(self):
        url = reverse("oidcfed_list")
        c = Client()
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
            trust_anchor=trust_anchor_ec
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

        self.intermediate_desc = FederationDescendant.objects.create(
            **intermediary_onboarding_data
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
            trust_anchor=trust_anchor_ec
        )

        self.assertTrue(trust_chain)
        self.assertTrue(trust_chain.final_metadata)

        for i in trust_chain.tree_of_trust.values():
            for ec in i:
                self.assertTrue(ec.is_valid)

        for ec in trust_chain.trust_path:
            self.assertTrue(ec.is_valid)

        self.assertTrue(len(trust_chain.trust_path) == 3)
        self.assertTrue((len(trust_chain.trust_path) - 2) == trust_chain.max_path_len)

        dumps = dumps_statements_from_trust_chain_to_db(trust_chain)

        self.assertTrue(isinstance(dumps, list) and len(dumps) == 5)

        self.assertTrue("sub" in dumps[0].get_entity_configuration_as_obj().payload)

        stored_trust_chain = TrustChain.objects.create(
            sub=trust_chain.subject,
            exp=trust_chain.exp_datetime,
            chain=trust_chain.serialize(),
            jwks = trust_chain.subject_configuration.jwks,
            metadata=trust_chain.final_metadata,
            parties_involved=[i.sub for i in trust_chain.trust_path],
            status="valid",
            trust_anchor=FetchedEntityStatement.objects.get(
                sub=trust_anchor_ec.sub, iss=trust_anchor_ec.sub
            ),
            is_active=True,
        )

    @override_settings(HTTP_CLIENT_SYNC=True)
    @patch("requests.get", return_value=EntityResponseWithIntermediateManyHints())
    def test_trust_chain_valid_with_intermediaries_many_authhints(self, mocked):

        trust_anchor_ec = self._create_federation_with_intermediary()

        self.rp_conf.authority_hints = [
            "http://intermediary-test",
            "http://that-faulty",
        ]
        self.rp_conf.save()

        trust_chain = trust_chain_builder(
            subject=self.rp.sub,
            trust_anchor=trust_anchor_ec
        )

        for ec in trust_chain.trust_path:
            self.assertTrue(ec.is_valid)

        self.assertTrue(len(trust_chain.trust_path) == 3)
        self.assertTrue((len(trust_chain.trust_path) - 2) == trust_chain.max_path_len)

    @override_settings(HTTP_CLIENT_SYNC=True)
    @patch("requests.get", return_value=EntityResponseWithIntermediate())
    def test_trust_chain_valid_with_intermediaries_and_trust_mark_filter(self, mocked):

        trust_anchor_ec = self._create_federation_with_intermediary()

        # the RP exposes a trust marks in its entity configuration
        self.rp_conf.trust_marks = [
            FederationEntityAssignedProfile.objects.filter(descendant=self.rp)
            .first()
            .trust_mark
        ]
        self.rp_conf.save()

        trust_chain = trust_chain_builder(
            subject=self.rp.sub,
            trust_anchor=trust_anchor_ec,
            required_trust_marks=["https://www.spid.gov.it/certification/rp"],
        )

        for ec in trust_chain.trust_path:
            self.assertTrue(ec.is_valid)

        self.assertTrue(trust_chain.verified_trust_marks)
        self.assertTrue(isinstance(trust_chain.verified_trust_marks[0], TrustMark))

        self.assertTrue(len(trust_chain.trust_path) == 3)
        self.assertTrue((len(trust_chain.trust_path) - 2) == trust_chain.max_path_len)

    @override_settings(HTTP_CLIENT_SYNC=True)
    @patch("requests.get", return_value=EntityResponseWithIntermediate())
    def test_trust_chain_with_missing_trust_mark(self, mocked):

        trust_anchor_ec = self._create_federation_with_intermediary()

        with self.assertRaises(InvalidRequiredTrustMark):
            trust_chain = trust_chain_builder(
                subject=self.rp.sub,
                trust_anchor=trust_anchor_ec,
                required_trust_marks=["https://www.spid.gov.it/certification/rp"],
            )

    @override_settings(HTTP_CLIENT_SYNC=True)
    @patch("requests.get", return_value=EntityResponseNoIntermediate())
    def test_trust_chain_valid_helpers(self, mocked):

        gctc = get_or_create_trust_chain(
            subject=rp_conf["sub"],
            trust_anchor=self.ta_conf.sub,
            # TODO
            # required_trust_marks: list = []
        )

        self.assertFalse(gctc.is_expired)
        self.assertTrue(gctc.is_valid)

    @override_settings(HTTP_CLIENT_SYNC=True)
    @patch("requests.get", return_value=EntityResponseNoIntermediate())
    def test_resolve_endpoint(self, mocked):
        gctc = get_or_create_trust_chain(
            subject=rp_conf["sub"],
            trust_anchor=self.ta_conf.sub,
            # TODO
            # required_trust_marks: list = []
        )

        url = reverse("oidcfed_resolve")

        c = Client()
        res = c.get(url, data={
                "sub": self.rp.sub, 
                "anchor": self.ta_conf.sub
            }
        )
        self.assertTrue(res.status_code == 200)
        verify_jws(res.content.decode(), self.ta_conf.jwks_fed[0])

    def test_trust_mark_status_endpoint(self):
        url = reverse("oidcfed_trust_mark_status")

        c = Client()
        res = c.post(
            url,
            data={
                "id": self.rp_assigned_profile.profile.profile_id,
                "sub": self.rp_assigned_profile.descendant.sub,
            },
        )
        self.assertTrue(res.status_code == 200)
        self.assertTrue(res.json() == {"active": True})

        res = c.post(
            url,
            data={
                "trust_mark": self.rp_assigned_profile.trust_mark["trust_mark"],
            },
        )
        self.assertTrue(res.status_code == 200)
        self.assertTrue(res.json() == {"active": True})

        res = c.get(
            url,
            data={
                "trust_mark": self.rp_assigned_profile.trust_mark["trust_mark"][1:],
            },
        )
        self.assertTrue(res.status_code == 200)
        self.assertTrue(res.json() == {"active": False})

        res = c.get(
            url,
            data={
                "id": self.rp_assigned_profile.profile.profile_id,
            },
        )
        self.assertTrue(res.status_code == 200)
        self.assertTrue(res.json() == {"active": False})

class TrustChainWithSignedJwksUriTest(TestCase):
    def setUp(self):
        self.ta_conf = FederationEntityConfiguration.objects.create(**ta_conf_data)
        
        _rp_conf = copy.deepcopy(rp_conf)
        _rp_conf['metadata']['openid_relying_party'].pop('jwks')
        _rp_conf['metadata']['openid_relying_party']['signed_jwks_uri'] = f"{_rp_conf['sub']}signed_jwks.jose"
        self.rp_conf = FederationEntityConfiguration.objects.create(**_rp_conf)

        self.rp_profile = FederationEntityProfile.objects.create(**RP_PROFILE)
        self.rp = FederationDescendant.objects.create(**rp_onboarding_data)
 
        self.rp_assigned_profile = FederationEntityAssignedProfile.objects.create(
            descendant=self.rp, profile=self.rp_profile, issuer=self.ta_conf
        )

    @override_settings(HTTP_CLIENT_SYNC=True)
    @patch("requests.get", return_value=EntityResponseNoIntermediateSignedJwksUri())
    def test_signed_jwks_uri(self, mocked):

        self.ta_conf.constraints = {"max_path_length": 0}
        self.ta_conf.save()

        jwt = get_entity_configurations(self.ta_conf.sub)
        trust_anchor_ec = EntityConfiguration(jwt[0])

        trust_chain = trust_chain_builder(
            subject=rp_onboarding_data["sub"],
            trust_anchor=trust_anchor_ec
        )
        _jwks = get_jwks(
            trust_chain.final_metadata['openid_relying_party'],
            trust_chain.subject_configuration.jwks
        )
        self.assertTrue(
            verify_jws(_jwks, self.rp_conf.jwks_fed[0])
        )
