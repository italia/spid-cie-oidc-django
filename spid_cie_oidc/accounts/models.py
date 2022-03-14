from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.sessions.models import Session
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    first_name = models.CharField(_("Name"), max_length=96, blank=True, null=True)
    last_name = models.CharField(_("Surname"), max_length=96, blank=True, null=True)
    is_active = models.BooleanField(_("active"), default=True)
    email = models.EmailField("email address", blank=True, null=True)
    origin = models.CharField(
        _("from which connector this user come from"),
        max_length=254,
        blank=True,
        null=True,
    )
    attributes = models.JSONField(default=dict, blank=True, null=True)

    class Meta:
        ordering = ["username"]
        verbose_name_plural = _("Users")

    def clear_sessions(self):  # pragma: no cover
        user_sessions = []
        for session in Session.objects.all():
            if str(self.pk) == session.get_decoded().get("_auth_user_id"):
                user_sessions.append(session.pk)
        return Session.objects.filter(pk__in=user_sessions).delete()

    def __str__(self):  # pragma: no cover
        return "{} {}".format(
            self.first_name or self.attributes.get('given_name'),
            self.last_name or self.attributes.get('family_name', "")
        )
