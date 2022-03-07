from .models import OnBoardingRegistration
from django.core.exceptions import ValidationError


def unique_entity_url(value):
    if OnBoardingRegistration.objects.filter(url_entity=value):
        raise ValidationError(f"{value} already onboarded")


def trust_anchor_validator(value):
    pass
    # raise ValidationError(f"{value} trust anchor not exist")
