from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models

from ...activity.constants import ArchiveActions
from ...core.models import BaseResourceModel


class Archive(BaseResourceModel):
    title = models.CharField(max_length=255, blank=True)
    content = models.TextField(null=True)
    archive_date = models.DateTimeField(null=True)
    location = models.CharField(max_length=255, null=True)
    future_action = models.CharField(max_length=255, null=True)
    author = models.ForeignKey(
        get_user_model(), on_delete=models.DO_NOTHING, default=None, null=True
    )
    tags = JSONField(default=dict, encoder=DjangoJSONEncoder)

    class Meta:
        permissions = [
            ("manage_archive", "All permissions for archive"),
        ]

    @property
    def actions(self):
        return ArchiveActions
