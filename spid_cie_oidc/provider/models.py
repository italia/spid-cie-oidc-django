from django.contrib.auth import get_user_model
from django.db import models
from spid_cie_oidc.entity.abstract_models import TimeStampedModel


class OidcSession(TimeStampedModel):
    """
    Store UserSessionInfo, ClientSessionInfo and Grant
    """

    user_uid = models.CharField(max_length=120)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,
                             blank=False, null=False)
    client_id = models.URLField(blank=True, null=True)

    authz_request = models.CharField(max_length=2048, blank=False, null=False)

    sub = models.CharField(max_length=254, blank=True, null=True)
    user_claims = models.JSONField(blank=True, null=True)

    revoked = models.BooleanField(default=False)

    auth_code = models.CharField(max_length=2048, blank=False, null= False)

    class Meta:
        verbose_name = ('User Session')
        verbose_name_plural = ('User Sessions')


class IssuedToken(TimeStampedModel):
    session = models.ForeignKey(OidcSession, on_delete=models.CASCADE)
    access_token = models.TextField(blank=True, null=True)
    id_token = models.TextField(blank=True, null=True)
    refresh_token = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = ('Issued Token')
        verbose_name_plural = ('Issued Tokens')

    @property
    def client_id(self):
        return self.session.client_id

    @property
    def user_uid(self):
        return self.session.user_uid
