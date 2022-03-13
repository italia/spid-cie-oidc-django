import logging

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext as _
from spid_cie_oidc.entity.abstract_models import TimeStampedModel


logger = logging.getLogger(__name__)


TEST_STATUS = (
    ("unknown", _("Unknown")),
    ("failed", _("Failed")),
    ("successfull", _("successfull")),
    ("error", _("Internal error"))
)


def context_media_path(instance, filename): # pragma: no cover
    # file will be uploaded to MEDIA_ROOT/...
    return (
        f'medias/{instance.client_id}/'
        f'{instance.report.pk}/'
        f'{filename}'
    )


class RelyingPartyReport(TimeStampedModel):
    """
        A test report about a RP
    """

    client_id = models.URLField(blank=True, null=True)
    user = models.ForeignKey(
        get_user_model(), on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text=_("Staff user that started the tests")
    )
    status = models.CharField(
        max_length=33,
        default = "unknown",
        help_text=_("status"),
        choices = TEST_STATUS
    )

    report = models.JSONField(max_length=4096, blank=True, default=dict)

    def __str__(self):
        return "{} {}".format(self.client_id, self.status)

    class Meta:
        verbose_name = "Relying Party Status"
        verbose_name_plural = "Relying Party Status"


class RelyingPartyTest(TimeStampedModel):
    """
        Single tests that belongs to a Report
    """

    report = models.ForeignKey(
        RelyingPartyReport, on_delete=models.CASCADE,
        help_text=_("")
    )
    name = models.CharField(max_length=256)
    category = models.CharField(max_length=256)
    code = models.CharField(max_length=256)
    http_status_code = models.PositiveIntegerField()

    screenshot = models.FileField(
        upload_to=context_media_path
    )
    log = models.TextField()
    note = models.TextField()

    status = models.CharField(
        max_length=33,
        default = "unknown",
        help_text=_("status"),
        choices = TEST_STATUS
    )

    @property
    def client_id(self):
        return self.report.client_id

    def __str__(self):
        return "{} {}".format(self.client_id, self.status)

    class Meta:
        verbose_name = "Relying Party Test"
        verbose_name_plural = "Relying Party Tests"
