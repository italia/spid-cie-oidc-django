from django import forms
from django.utils.translation import gettext_lazy as _


class TestingPageAttributesForm(forms.Form):

    attributes = forms.JSONField(
        initial=dict,
        label="attributes"
    )


class TestingPageChecksForm(forms.Form):

    CHOICES = (
         ('send_auth_code_no_code', _('[auth code] send an auth code response without code')),
         ('send_auth_code_no_state', _('[auth code] send an auth code without state')),
         ('unsigned_id_token', _('[token endpoint] release an unsigned id token')),
         ('id_token_with_wrong_signature', _('[token endpoint] release an id token with a wrong signature'))
    )

    test = forms.ChoiceField(
        choices=CHOICES,
        widget=forms.RadioSelect,
        label="select",
        # error_messages={"required": _("Select an item")},
        required=False
    )
