import json
import logging
import uuid

from django.contrib.auth import get_user_model
from django.db import models

from spid_cie_oidc.entity.jwtse import unpad_jwt_payload


logger = logging.getLogger(__name__)


class OidcAuthentication(models.Model):
    client_id = models.CharField(max_length=255)
    state = models.CharField(max_length=255, unique=True, default=uuid.uuid4)
    endpoint = models.URLField(blank=True, null=True)
    data = models.TextField(blank=True, null=True)
    successful = models.BooleanField(default=False)

    provider_id = models.CharField(max_length=255, blank=True, null=True)
    provider_configuration = models.JSONField(
        blank=True, null=True, default=dict
    )

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "OIDC Authentication"
        verbose_name_plural = "OIDC Authentications"

    def __str__(self):
        return f"{self.client_id} {self.state} to {self.endpoint}"


class OidcAuthenticationToken(models.Model):
    user = models.ForeignKey(
        get_user_model(), on_delete=models.SET_NULL, blank=True, null=True
    )
    authz_request = models.ForeignKey(OidcAuthentication, on_delete=models.CASCADE)
    code = models.CharField(max_length=255, blank=True, null=True)
    access_token = models.TextField(blank=True, null=True)
    id_token = models.TextField(blank=True, null=True)
    refresh_token = models.TextField(blank=True, null=True)

    scope = models.CharField(max_length=255, blank=True, null=True)
    token_type = models.CharField(max_length=255, blank=True, null=True)
    expires_in = models.IntegerField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    revoked = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.authz_request} {self.code}"

    def token_preview(self, token):
        if token:
            try:
                data = unpad_jwt_payload(token)
                dumps = json.dumps(data, indent=2)
                return dumps  # mark_safe(dumps.replace("\n", "<br>").replace(" ", "&nbsp"))
            except Exception as e:
                logger.error(e)
        else:
            return '--'

    @property
    def access_token_preview(self):
        return self.token_preview(self.access_token)

    @property
    def id_token_preview(self):
        return self.token_preview(self.id_token)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.authz_request.successful = True
        self.authz_request.save()
