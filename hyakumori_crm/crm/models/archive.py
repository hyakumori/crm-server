from django.db import models

from ...core.models import BaseResourceModel


class Archive(BaseResourceModel):
    archive_date = models.DateField(blank=True)
