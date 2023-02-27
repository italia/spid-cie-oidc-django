from copy import deepcopy

from django.core.exceptions import ValidationError
from django.test import TestCase
from spid_cie_oidc.authority.tests.settings import (
    RP_METADATA_JWK1,
    RP_METADATA_JWK1_pub
)
from spid_cie_oidc.entity.tests.op_metadata_settings import OP_METADATA
from spid_cie_oidc.entity.tests.rp_metadata_settings import RP_METADATA_SPID
from spid_cie_oidc.entity.validators import (
    validate_entity_metadata,
    validate_metadata_algs,
    validate_private_jwks,
    validate_public_jwks
)


class ValidatrTest(TestCase):

    def setUp(self):
        pass

    def test_validate_public_jwks_with_private_key(self):
        with self.assertRaises(Exception):
            validate_public_jwks(RP_METADATA_JWK1)

    def test_validate_private_jwks_with_public_key(self):
        with self.assertRaises(Exception):
            validate_private_jwks(RP_METADATA_JWK1_pub)

    def test_validate_public_jwks(self):
        validate_public_jwks(RP_METADATA_JWK1_pub)

    def test_validate_private_jwks(self):
        validate_private_jwks(RP_METADATA_JWK1)

    def test_validate_metadata_algs_ok(self):
        op_md = {}
        op_md["openid_provider"] = OP_METADATA
        validate_metadata_algs(op_md)

    def test_validate_metadata_algs_with_error(self):
        OP_METADATA_NO_CORRECT = deepcopy(OP_METADATA)
        OP_METADATA_NO_CORRECT["token_endpoint_auth_signing_alg_values_supported"] = ["ciao"]
        op_md = {}
        op_md["openid_provider"] = OP_METADATA_NO_CORRECT
        with self.assertRaises(ValidationError):
            validate_metadata_algs(op_md)

    def test_validate_entity_op_metadata(self):
        op_md = {}
        op_md["openid_provider"] = deepcopy(OP_METADATA)
        validate_entity_metadata(op_md)

    def test_validate_entity_no_valid_op_metadata(self):
        op_md = {}
        op_md["openid_provider"] = deepcopy(OP_METADATA)
        op_md["openid_provider"].pop("issuer")
        with self.assertRaises(ValidationError):
            validate_entity_metadata(op_md)

    def test_validate_entity_rp_metadata(self):
        rp_md = {}
        rp_md["openid_relying_party"] = deepcopy(RP_METADATA_SPID)
        validate_entity_metadata(rp_md)

    def test_validate_entity_no_valid_rp_metadata(self):
        rp_md = {}
        rp_md["openid_relying_party"] = deepcopy(RP_METADATA_SPID)
        rp_md["openid_relying_party"].pop("grant_types")
        with self.assertRaises(ValidationError):
            validate_entity_metadata(rp_md)

    def test_validate_entity_no_entity_type(self):
        rp_md = {}
        rp_md = deepcopy(RP_METADATA_SPID)
        with self.assertRaises(ValidationError):
            validate_entity_metadata(rp_md)

    
