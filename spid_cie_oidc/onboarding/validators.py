from .models import OnBoardingRegistration
from django.core.exceptions import ValidationError


def unique_entity_url(value):
    if OnBoardingRegistration.objects.filter(url_entity=value):
        raise ValidationError(f"{value} already onboarded")
