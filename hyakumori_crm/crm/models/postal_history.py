from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models

from ...core.models import BaseResourceModel, BaseRelationModel
from ...activity.constants import PostalHistoryActions


class PostalHistory(BaseResourceModel):
    title = models.CharField(max_length=255, blank=True)
    content = models.TextField(null=True)
    archive_date = models.DateTimeField(null=True)
    author = models.ForeignKey(
        get_user_model(), on_delete=models.DO_NOTHING, default=None, null=True
    )
    tags = JSONField(default=dict, encoder=DjangoJSONEncoder)

    REPR_FIELD = "title"
    REPR_NAME = "書類郵送履歴タイトル"

    class Meta:
        permissions = [
            ("manage_postalhistory", "All permissions for postal history"),
        ]

    @property
    def actions(self):
        return PostalHistoryActions

    def repr_name(self):
        return self.title


class PostalHistoryForest(BaseRelationModel):
    postalhistory = models.ForeignKey("PostalHistory", on_delete=models.PROTECT)
    forest = models.ForeignKey("Forest", on_delete=models.CASCADE)


class PostalHistoryCustomer(BaseRelationModel):
    postalhistory = models.ForeignKey("PostalHistory", on_delete=models.PROTECT)
    customer = models.ForeignKey("Customer", on_delete=models.CASCADE)


class PostalHistoryCustomerContact(BaseRelationModel):
    postalhistorycustomer = models.ForeignKey(
        "PostalHistoryCustomer", on_delete=models.CASCADE
    )
    customercontact = models.ForeignKey("CustomerContact", on_delete=models.CASCADE)


class PostalHistoryUser(BaseRelationModel):
    postalhistory = models.ForeignKey("PostalHistory", on_delete=models.PROTECT)
    user = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)
