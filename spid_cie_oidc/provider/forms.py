from django import forms
from django.utils.translation import gettext_lazy as _


class AuthLoginForm(forms.Form):
    """
    The User Authentication Form for an Authorized request
    """

    username = forms.CharField(
        initial="",
        label=_("Username"),
        error_messages={"required": _("Enter your username")},
    )
    password = forms.CharField(
        initial="",
        label=_("Password"),
        error_messages={"required": _("Enter your password")},
        widget=forms.PasswordInput(),
    )
    # when a prue SSO will be enabled.
    # forget_agreement = forms.BooleanField(label=_("Delete previous agreement"),
    # required=False,
    # localize=True)
    # forget_login = forms.BooleanField(label=_("Forget access"),
    # required=False,
    # localize=True)


class AuthzHiddenForm(forms.Form):
    """
    A hidden form to carry the original authz request
    """
    authz_request_object = forms.CharField(widget=forms.HiddenInput())


class ConsentPageForm(forms.Form):
    agree = forms.BooleanField(initial=True, widget=forms.HiddenInput())
