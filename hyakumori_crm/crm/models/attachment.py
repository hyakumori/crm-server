import os

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from ...core.models import BaseResourceModel


def attachment_upload(instance, filename):
    """Stores the attachment in a "per module/appname/primary key" folder"""
    return "attachments/{app}_{model}/{pk}/{filename}".format(
        app=instance.content_object._meta.app_label,
        model=instance.content_object._meta.object_name.lower(),
        pk=instance.content_object.pk,
        filename=filename,
    )


class AttachmentManager(models.Manager):
    def attachments_for_object(self, obj):
        object_type = ContentType.objects.get_for_model(obj)
        return self.filter(content_type__pk=object_type.pk, object_id=obj.pk)


class Attachment(BaseResourceModel):
    objects = AttachmentManager()

    content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING)
    object_id = models.CharField(max_length=255)
    content_object = GenericForeignKey("content_type", "object_id")
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="created_attachments",
        verbose_name="creator",
        on_delete=models.DO_NOTHING,
    )
    attachment_file = models.FileField("attachment", upload_to=attachment_upload)

    class Meta:
        verbose_name = "attachment"
        verbose_name_plural = "attachments"
        ordering = ["-created_at"]
        permissions = (
            ("delete_foreign_attachments", "Can delete foreign attachments"),
        )

    def __str__(self):
        return "{username} attached {filename}".format(
            username=self.creator, filename=self.attachment_file.name,
        )

    @property
    def filename(self):
        return os.path.split(self.attachment_file.name)[1]
