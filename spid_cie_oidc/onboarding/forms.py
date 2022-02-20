from django import forms
from django.utils.translation import gettext_lazy as _


class OnboardingRegistrationForm(forms.Form):
    
    organization_name = forms.CharField(
        label= _("organization Name"),
        error_messages={'required' : _('Enter your organization name')}
    )

    url_entity = forms.URLField(
        initial='https://',
        label=_("url of the entity"),
        error_messages={'required' : _('Enter your url of the entity')}
    )

    authn_buttons_page_url = forms.URLField(
        initial='http://',
        label=_("url of the page where the SPID/CIE button is available"),
        error_messages={
            'required' : _('Enter the url of the page where the SPID/CIE button is available')}
    )

    public_jwks = forms.CharField(
        label=_("public jwks of the entities"),
        error_messages={
            'required' : _('Enter the public jwks of the entities')}
    )
