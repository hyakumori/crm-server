from django.db import models

from ...core.models import BaseRelationModel
from .archive import Archive
from .customer import Contact, Customer
from .forest import Forest


class CustomerContact(BaseRelationModel):
    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING)
    contact = models.ForeignKey(Contact, on_delete=models.DO_NOTHING)
    is_basic = models.BooleanField(
        default=False
    )  # if True, will show in the list of Owners for select direct owners

    @property
    def is_default(self):
        return self.attributes["is_default"]

    @property
    def relative_type(self):
        if "relative_type" in self.attributes:
            return None

        return self.attributes["relative_type"]

    def set_relative_type(self, value):
        self.attributes["relative_type"] = value
        return self


class ForestCustomer(BaseRelationModel):
    forest = models.ForeignKey(Forest, on_delete=models.DO_NOTHING)
    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING)
    contact = models.ForeignKey(Contact, on_delete=models.DO_NOTHING)


class ArchiveForest(BaseRelationModel):
    archive = models.ForeignKey(Archive, on_delete=models.DO_NOTHING)
    forest = models.ForeignKey(Forest, on_delete=models.DO_NOTHING)


class ArchiveCustomer(BaseRelationModel):
    archive = models.ForeignKey(Archive, on_delete=models.DO_NOTHING)
    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING)
    contact = models.ForeignKey(Contact, on_delete=models.DO_NOTHING)
