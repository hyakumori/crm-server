from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _

from hyakumori_crm.core.models import UUIDPrimary, TimestampMixin, AttributesMixin


class TagSetting(UUIDPrimary, TimestampMixin, AttributesMixin):
    content_type = models.ForeignKey(
        "contenttypes.ContentType",
        related_name="+",
        verbose_name=_("content type"),
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )
    name = models.CharField(max_length=255, blank=False, null=False, verbose_name=_("tag name"))
    code = models.CharField(max_length=255, blank=False, null=False,
                            verbose_name=_("slug alike sanitized"))
    user = models.ForeignKey(
        get_user_model(),
        verbose_name=_("user"),
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="authored_tagsetting",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("tag setting")
        verbose_name_plural = _("tag settings")
        constraints = [
            models.UniqueConstraint(fields=["name", "code", "content_type"], name="unique_tag_setting"),
        ]

    def __str__(self):
        return _("TagSettings, id: {id}").format(id=self.id)
