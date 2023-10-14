from copy import deepcopy
from django.conf import settings
from django.utils.translation import gettext as _
from spid_cie_oidc.entity.schemas.op_metadata import (
    OPMetadataCie,
    OPMetadataSpid
)
from spid_cie_oidc.provider.schemas.authn_requests import (
    AcrValues,
    AuthenticationRequestCie,
    AuthenticationRequestDoc,
    AuthenticationRequestSpid
)
from spid_cie_oidc.provider.schemas.authn_response import AuthenticationErrorResponse, AuthenticationErrorResponseCie, \
    AuthenticationResponse, AuthenticationResponseCie
from spid_cie_oidc.provider.schemas.introspection_request import IntrospectionRequest
from spid_cie_oidc.provider.schemas.introspection_response import IntrospectionErrorResponseCie, \
    IntrospectionErrorResponseSpid, IntrospectionResponse
from spid_cie_oidc.provider.schemas.revocation_request import RevocationRequest
from spid_cie_oidc.provider.schemas.revocation_response import RevocationErrorResponse
from spid_cie_oidc.provider.schemas.token_requests import TokenAuthnCodeRequest, TokenRefreshRequest
from spid_cie_oidc.provider.schemas.token_response import TokenErrorResponse, TokenRefreshResponse, TokenResponse


OIDCFED_PROVIDER_PROFILES_MEDIA = getattr(
    settings,
    "OIDCFED_PROVIDER_PROFILES_MEDIA",
    {
        "spid": {
            "logo": "svg/spid-logo-c-lb.svg",
            "arc_position": ""
        },
        "cie": {
            "logo": "svg/logo-cie.svg",
            "arc_position": "mt-5"
        },
    },
)
OIDCFED_PROVIDER_ATTRIBUTES_SPID_MAP = {
    "https://attributes.eid.gov.it/spid_code": (
        {
            "func": "spid_cie_oidc.provider.processors.spidCode",
            "kwargs": {"salt": "signiicusenz"},
        },
    ),
    "given_name": ("given_name",),
    "family_name": ("family_name",),
    "place_of_birth": ("place_of_birth",),
    "birthdate": ("birthdate",),
    "gender": ("gender",),
    "https://attributes.eid.gov.it/company_name": ("company_name",),
    "https://attributes.eid.gov.it/registered_office": ("registered_office",),
    "https://attributes.eid.gov.it/fiscal_number": ("fiscal_number", ),
    "https://attributes.eid.gov.it/company_fiscal_number": ("company_fiscal_number",),
    "https://attributes.eid.gov.it/vat_number": ("vat_number",),
    "document_details": ("document_details",),
    "phone_number": ("phone_number",
        "mobile_phone",
        "phone",
        "telephone",
    ),
    "email": ("email",),
    "https://attributes.eid.gov.it/e_delivery_service": ("e_delivery_service",),
    "https://attributes.eid.gov.it/eid_exp_date": ("eid_exp_date",),
    "address": ("address",),
}

OIDCFED_PROVIDER_ATTRIBUTES_CIE_MAP = {
    "given_name": ("name", "given_name"),
    "family_name": ("family_name", "surname"),
    "email": ("email",),
    "fiscal_number": ("fiscal_number", "tin"),
    "email_verified": ("email",),
    "gender": ("gender",),
    "birthdate": ("date_of_birth",),
    "phone_number": ("mobile_phone", "phone", "telephone"),
    "phone_number_verified": ("mobile_phone", "phone", "telephone"),
    "address": ("address",),
    "place_of_birth": ("place_of_birth",),
    # "document_details":  ,
    # "e_delivery_service":  ,
    "physical_phone_number": ("mobile_phone", "phone", "telephone"),
}

OIDCFED_PROVIDER_ATTRIBUTES_MAP = deepcopy(OIDCFED_PROVIDER_ATTRIBUTES_SPID_MAP)
OIDCFED_PROVIDER_ATTRIBUTES_MAP.update(OIDCFED_PROVIDER_ATTRIBUTES_CIE_MAP)

OIDCFED_PROVIDER_PROFILES_ID_TOKEN_CLAIMS = dict(
    spid = dict(),
    cie = OIDCFED_PROVIDER_ATTRIBUTES_CIE_MAP
)

OIDCFED_PROVIDER_PROFILES = getattr(
    settings,
    "OIDCFED_PROVIDER_PROFILES",
    {
        "spid": {
            "authorization_request": AuthenticationRequestSpid,
            "authorization_request_doc": AuthenticationRequestDoc,
            "authorization_response": AuthenticationResponse,
            "authorization_error_response": AuthenticationErrorResponse,
            "op_metadata": OPMetadataSpid,
            "authorization_code": TokenAuthnCodeRequest,
            "authorization_code_response": TokenResponse,
            "refresh_token": TokenRefreshRequest,
            "refresh_token_response": TokenRefreshResponse,
            "token_error_response": TokenErrorResponse,
            "revocation_request": RevocationRequest,
            "revocation_response": RevocationErrorResponse,
            "introspection_request" : IntrospectionRequest,
            "introspection_response" : IntrospectionResponse,
            "introspection_error_response" : IntrospectionErrorResponseSpid,
        },
        "cie": {
            "authorization_request": AuthenticationRequestCie,
            "authorization_request_doc": AuthenticationRequestDoc,
            "authorization_response": AuthenticationResponseCie,
            "authorization_error_response": AuthenticationErrorResponseCie,
            "op_metadata": OPMetadataCie,
            "authorization_code": TokenAuthnCodeRequest,
            "authorization_code_response": TokenResponse,
            "refresh_token": TokenRefreshRequest,
            "refresh_token_response": TokenRefreshResponse,
            "token_error_response": TokenErrorResponse,
            "revocation_request": RevocationRequest,
            "revocation_response": RevocationErrorResponse,
            "introspection_request" : IntrospectionRequest,
            "introspection_response" : IntrospectionResponse,
            "introspection_error_response" : IntrospectionErrorResponseCie,
        },
    },
)

OIDCFED_PROVIDER_SALT = getattr(settings, "OIDCFED_PROVIDER_SALT", "CHANGEME")
OIDCFED_DEFAULT_PROVIDER_PROFILE = getattr(settings, "OIDCFED_PROVIDER_PROFILE", "spid")

OIDCFED_PROVIDER_MAX_REFRESH = getattr(settings, "OIDCFED_PROVIDER_MAX_REFRESH", 1)
OIDCFED_PROVIDER_HISTORY_PER_PAGE = getattr(settings, "OIDCFED_PROVIDER_HISTORY_PER_PAGE", 50)

# lifetime of validity of an auth code
OIDCFED_PROVIDER_AUTH_CODE_MAX_AGE = getattr(
    settings,
    "OIDCFED_PROVIDER_AUTH_CODE_MAX_AGE",
    10
)

OIDCFED_PROVIDER_MAX_CONSENT_TIMEFRAME = getattr(
    settings,
    "OIDCFED_PROVIDER_MAX_CONSENT_TIMEFRAME",
    2
)

OIDCFED_PROVIDER_PROFILES_DEFAULT_ACR = getattr(
    settings,
    "OIDCFED_PROVIDER_PROFILES_DEFAULT_ACR",
    dict(
        spid = AcrValues.l2.value,
        cie = AcrValues.l2.value
    )
)

OIDCFED_PROVIDER_PROFILES_ACR_4_REFRESH = getattr(
    settings,
    "OIDCFED_PROVIDER_PROFILES_ACR_4_REFRESH",
    dict(
        spid = [AcrValues.l1.value],
        cie = [AcrValues.l1.value]
    )
)


OIDCFED_ATTRNAME_I18N = {
    # SPID
    "given_name": _("Name"),
    "family_name": _("Family name"),
    "place_of_birth": _("Place of birth"),
    "birthdate": _("Date of birth"),
    "gender": _("Gender"),
    "https://attributes.eid.gov.it/company_name": _("Company Name"),
    "https://attributes.eid.gov.it/registered_office": _("Registered Office"),
    "https://attributes.eid.gov.it/fiscal_number": _("Tax payer id"),
    "https://attributes.eid.gov.it/vat_number": _("Vat number"),
    "document_details": _("Id card"),
    "phone_number": _("Mobile phone"),
    "email": _("Email"),
    "address": _("Address"),
    "https://attributes.eid.gov.it/eid_exp_date": _("Expiration date"),
    "https://attributes.eid.gov.it/e_delivery_service": _("Digital address"),

    # CIE
    "given_name": _("Name"),
    "family_name": _("Family name"),
    "email": _("Email"),
    "fiscal_number": _("Tax payer id"),
    "email_verified": _("Email verified"),
    "gender": _("Gender"),
    "birthdate": _("Date of birth"),
    "phone_number": _("Phone number"),
    "phone_number_verified": _("Verified phone"),
    "address": _("Address"),
    "place_of_birth": _("Place of birth"),
    # "document_details":  ,
    # "e_delivery_service":  ,
    "physical_phone_number": _("Phone number"),
}
