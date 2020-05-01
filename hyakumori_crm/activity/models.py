from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import ugettext_lazy as _

from hyakumori_crm.core.models import UUIDPrimary
from ..crm.models.message_template import MessageTemplate


class ActionLog(UUIDPrimary):
    content_type = models.ForeignKey(
        "contenttypes.ContentType",
        related_name="+",
        verbose_name=_("content type"),
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )
    object_pk = models.CharField(
        verbose_name=_("object pk"),
        max_length=255,
        blank=True,
        null=True,
        db_index=True,
    )
    user = models.ForeignKey(
        get_user_model(),
        verbose_name=_("user"),
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="actionlogs",
    )
    template_name = models.CharField(max_length=255, blank=False, null=False)
    template_data = JSONField(verbose_name=_("template rendering data"), blank=True, null=True)
    changes = JSONField(blank=True, verbose_name=_("change diff"))
    remote_ip = models.GenericIPAddressField(verbose_name=_("remote IP"), blank=True, null=True)
    created_at = models.DateTimeField(verbose_name=_("created at"), auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("log action")
        verbose_name_plural = _("log actions")

    def __str__(self):
        return _("Logged action, id: {id}").format(id=self.id)

    def get_edited_object(self):
        """Returns the edited object represented by this log entry"""
        return self.content_type.get_object_for_this_type(pk=self.object_pk)
