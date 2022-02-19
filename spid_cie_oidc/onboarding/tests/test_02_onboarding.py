from django.test import TestCase, Client, override_settings
from django.urls import reverse

from spid_cie_oidc.entity.jwtse import verify_jws
from spid_cie_oidc.entity.models import *
from spid_cie_oidc.entity.trust_chain import trust_chain_builder
from spid_cie_oidc.entity.statements import EntityConfiguration, get_entity_configurations
from spid_cie_oidc.onboarding.models import *

from spid_cie_oidc.entity.tests.settings import *
from spid_cie_oidc.onboarding.tests.settings import *
from spid_cie_oidc.onboarding.tests.mocked_responses import *

from unittest.mock import patch


class OnBoardingTest(TestCase):

    def setUp(self):
        self.ta_conf = FederationEntityConfiguration.objects.create(**ta_conf_data)
        self.rp_conf = FederationEntityConfiguration.objects.create(**rp_conf)

        self.rp_profile = FederationEntityProfile.objects.create(**RP_PROFILE)
        self.rp = FederationDescendant.objects.create(**rp_onboarding_data)

        self.rp_jwk = PublicJwk.objects.create(
            jwk = self.rp_conf.public_jwks[0],
            kid = self.rp_conf.public_jwks[0]['kid']
        )
        FederationDescendantJwk.objects.create(
            descendant=self.rp,
            jwk = self.rp_jwk
        )
        FederationEntityAssignedProfile.objects.create(
            descendant = self.rp,
            profile = self.rp_profile,
            issuer = self.ta_conf
        )

    def test_fetch_endpoint(self):
        url = reverse('oidcfed_fetch')
        c = Client()
        res = c.get(url, data={'sub': self.rp.sub})
        data = verify_jws(res.content.decode(), self.ta_conf.jwks[0])
        self.assertTrue(
            data['jwks']
        )

    def test_list_endpoint(self):
        url = reverse('oidcfed_list')
        c = Client()
        res = c.get(url, data={'is_leaf': True})
        self.assertTrue(
            res.json()[0] == self.rp.sub
        )
        res = c.get(url, data={'is_leaf': False})
        self.assertFalse(res.json())

    @override_settings(HTTP_CLIENT_SYNC=True)
    @patch("requests.get", return_value=EntityResponse())
    def test_trust_chain_valid_no_intermediaries(self, mocked):
        jwt = get_entity_configurations(self.ta_conf.sub)
        trust_anchor_ec = EntityConfiguration(jwt[0])
        
        trust_chain = trust_chain_builder(
            subject = rp_onboarding_data['sub'],
            trust_anchor = trust_anchor_ec,
            metadata_type = 'openid_relying_party'
        )
        self.assertTrue(trust_chain)
        self.assertTrue(trust_chain.final_metadata)

    @override_settings(HTTP_CLIENT_SYNC=True)
    @patch("requests.get", return_value=IntermediateEntityResponse())
    def test_trust_chain_valid_with_intermediaries(self, mocked):
        jwt = get_entity_configurations(self.ta_conf.sub)
        trust_anchor_ec = EntityConfiguration(jwt[0])

        self.intermediate = FederationEntityConfiguration.objects.create(
            **intermediary_conf
        )
        self.intermediate_jwk = PublicJwk.objects.create(
            jwk = self.intermediate.public_jwks[0],
            kid = self.intermediate.public_jwks[0]['kid']
        )
        self.intermediate_desc = FederationDescendant.objects.create(
            **intermediary_onboarding_data
        )
        FederationDescendantJwk.objects.create(
            descendant=self.intermediate_desc,
            jwk = self.intermediate_jwk
        )
        FederationEntityAssignedProfile.objects.create(
            descendant = self.rp,
            profile = self.rp_profile,
            issuer = self.intermediate
        )
        self.rp_conf.authority_hints = [intermediary_conf['sub']]
        self.rp_conf.save()

        trust_chain = trust_chain_builder(
            subject = self.rp.sub,
            trust_anchor = trust_anchor_ec,
            metadata_type = 'openid_relying_party'
        )
        self.assertTrue(trust_chain)
        self.assertTrue(trust_chain.final_metadata)
