import hashlib
import logging

from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _
from spid_cie_oidc.entity.abstract_models import TimeStampedModel
from spid_cie_oidc.provider.settings import OIDCFED_PROVIDER_SALT

logger = logging.getLogger(__name__)


class OidcSession(TimeStampedModel):
    """
        Store UserSessionInfo, ClientSessionInfo and Grant
    """

    user_uid = models.CharField(max_length=120)
    user = models.ForeignKey(
        get_user_model(), on_delete=models.SET_NULL, blank=True, null=True
    )
    client_id = models.URLField(blank=True, null=True)
    sid = models.CharField(
        max_length=1024, blank=True, null=True,
        help_text=_("django session key")
    )
    nonce = models.CharField(max_length=2048, blank=False, null=False)
    authz_request = models.JSONField(max_length=2048, blank=False, null=False)

    revoked = models.BooleanField(default=False)
    auth_code = models.CharField(max_length=2048, blank=False, null=False)
    acr = models.CharField(max_length=1024, blank=False, null=False)

    def set_sid(self, request):
        try:
            Session.objects.get(session_key=request.session.session_key)
            self.sid = request.session.session_key
        except Exception:
            logger.warning(
                f"Error setting SID for OidcSession {self} "
                "due to multiple authentication with different users with "
                "the same browser."
            )
            self.sid = self.auth_code
        self.save()

    def revoke(self, destroy_session=True):
        session = Session.objects.filter(session_key=self.sid)
        if session and destroy_session:
            session.delete()
        self.revoked = True
        iss_tokens = IssuedToken.objects.filter(session=self)
        iss_tokens.update(revoked=True)
        self.save()

    def pairwised_sub(self):
        return hashlib.sha256(
            f"{self.user_uid}{self.client_id}{OIDCFED_PROVIDER_SALT}".encode()
        ).hexdigest()

    def public_sub(self):
        return hashlib.sha256(
            f"{self.user_uid}{OIDCFED_PROVIDER_SALT}".encode()
        ).hexdigest()

    def __str__(self):
        return "{} {}".format(self.user_uid, self.auth_code)

    class Meta:
        verbose_name = "User Session"
        verbose_name_plural = "User Sessions"
        unique_together = ("client_id", "nonce")
        ordering = ["-created"]


class IssuedToken(TimeStampedModel):
    session = models.ForeignKey(OidcSession, on_delete=models.CASCADE)
    access_token = models.TextField(blank=True, null=True)
    id_token = models.TextField(blank=True, null=True)
    refresh_token = models.TextField(blank=True, null=True)
    expires = models.DateTimeField()
    revoked = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Issued Token"
        verbose_name_plural = "Issued Tokens"

    @property
    def client_id(self):
        return self.session.client_id

    @property
    def user_uid(self):
        return self.session.user_uid

    @property
    def expired(self):
        return timezone.localtime() >= self.expires

    @property
    def is_revoked(self):
        return self.session.revoked or self.revoked

    def __str__(self):
        return "{} @ {}".format(self.session.user_uid, self.session.client_id)
