from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models

from ...activity.constants import ArchiveActions
from ...core.models import BaseResourceModel, BaseRelationModel


class Archive(BaseResourceModel):
    title = models.CharField(max_length=255, blank=True)
    content = models.TextField(null=True)
    archive_date = models.DateTimeField(null=True)
    location = models.CharField(max_length=255, null=True)
    future_action = models.TextField(null=True)
    author = models.ForeignKey(
        get_user_model(), on_delete=models.DO_NOTHING, default=None, null=True
    )
    tags = JSONField(default=dict, encoder=DjangoJSONEncoder)

    REPR_FIELD = "title"
    REPR_NAME = "協議履歴タイトル"

    class Meta:
        permissions = [
            ("manage_archive", "All permissions for archive"),
        ]

    @property
    def actions(self):
        return ArchiveActions

    def repr_name(self):
        return self.title


class ArchiveForest(BaseRelationModel):
    archive = models.ForeignKey("Archive", on_delete=models.PROTECT)
    forest = models.ForeignKey("Forest", on_delete=models.CASCADE)

    class Meta:
        permissions = [
            ("manage_archivecustomer", "All permissions for archive forest"),
        ]


class ArchiveCustomer(BaseRelationModel):
    archive = models.ForeignKey("Archive", on_delete=models.PROTECT)
    customer = models.ForeignKey("Customer", on_delete=models.CASCADE)


class ArchiveCustomerContact(BaseRelationModel):
    archivecustomer = models.ForeignKey("ArchiveCustomer", on_delete=models.CASCADE)
    customercontact = models.ForeignKey("CustomerContact", on_delete=models.CASCADE)


class ArchiveUser(BaseRelationModel):
    archive = models.ForeignKey("Archive", on_delete=models.PROTECT)
    user = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)
