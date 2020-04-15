from django.db import models

from ...core.models import BaseResourceModel


class Archive(BaseResourceModel):
    archive_date = models.DateField(blank=True)

    class Meta:
        permissions = [("manage_archive", "All permissions for customer"), ]
