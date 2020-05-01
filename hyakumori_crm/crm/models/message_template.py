from django.db import models

from hyakumori_crm.core.models import UUIDPrimary, TimestampMixin, AttributesMixin


class MessageTemplate(UUIDPrimary, AttributesMixin, TimestampMixin):
    content_type = models.ForeignKey(
        "contenttypes.ContentType",
        related_name="+",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )
    name = models.CharField(max_length=255, blank=False, null=False)
    template = models.TextField(blank=True)
    language = models.CharField(max_length=10, default="ja_JP")
