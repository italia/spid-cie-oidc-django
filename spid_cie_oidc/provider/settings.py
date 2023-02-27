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
from spid_cie_oidc.provider.schemas.authn_response import AuthenticationErrorResponse, AuthenticationErrorResponseCie, AuthenticationResponse, AuthenticationResponseCie
from spid_cie_oidc.provider.schemas.introspection_request import IntrospectionRequest
from spid_cie_oidc.provider.schemas.introspection_response import IntrospectionErrorResponseCie, IntrospectionErrorResponseSpid, IntrospectionResponse
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
    "https://attributes.spid.gov.it/spidCode": (
        {
            "func": "spid_cie_oidc.provider.processors.spidCode",
            "kwargs": {"salt": "signiicusenz"},
        },
    ),
    "https://attributes.spid.gov.it/name": ("name", "given_name"),
    "https://attributes.spid.gov.it/familyName": ("family_name", "surname"),
    "https://attributes.spid.gov.it/placeOfBirth": ("place_of_birth",),
    "https://attributes.spid.gov.it/countyOfBirth": ("county_of_birth",),
    "https://attributes.spid.gov.it/dateOfBirth": ("date_of_birth", "birthdate"),
    "https://attributes.spid.gov.it/gender": ("gender",),
    "https://attributes.spid.gov.it/companyName": ("company_name",),
    "https://attributes.spid.gov.it/registeredOffice": ("registered_office",),
    "https://attributes.spid.gov.it/fiscalNumber": ("fiscal_number", "tin"),
    "https://attributes.spid.gov.it/ivaCode": ("iva_code",),
    "https://attributes.spid.gov.it/idCard": ("id_card",),
    "https://attributes.spid.gov.it/mobilePhone": (
        "mobile_phone",
        "phone",
        "telephone",
    ),
    "https://attributes.spid.gov.it/email": ("email",),
    "https://attributes.spid.gov.it/address": ("address",),
    "https://attributes.spid.gov.it/expirationDate": ("expiration_date",),
    "https://attributes.spid.gov.it/digitalAddress": ("digital_address",),
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
    "https://attributes.spid.gov.it/name": _("Name"),
    "https://attributes.spid.gov.it/familyName": _("Family name"),
    "https://attributes.spid.gov.it/placeOfBirth": _("Place of birth"),
    "https://attributes.spid.gov.it/countyOfBirth": _("County of birth",),
    "https://attributes.spid.gov.it/dateOfBirth": _("Date of birth"),
    "https://attributes.spid.gov.it/gender": _("Gender"),
    "https://attributes.spid.gov.it/companyName": _("Company Name"),
    "https://attributes.spid.gov.it/registeredOffice": _("Registered Office"),
    "https://attributes.spid.gov.it/fiscalNumber": _("Tax payer id"),
    "https://attributes.spid.gov.it/ivaCode": _("Vat number"),
    "https://attributes.spid.gov.it/idCard": _("Id card"),
    "https://attributes.spid.gov.it/mobilePhone": _("Mobile phone"),
    "https://attributes.spid.gov.it/email": _("Email"),
    "https://attributes.spid.gov.it/address": _("Address"),
    "https://attributes.spid.gov.it/expirationDate": _("Expiration date"),
    "https://attributes.spid.gov.it/digitalAddress": _("Digital address"),

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
