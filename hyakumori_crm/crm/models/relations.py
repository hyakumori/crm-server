from django.db import models

from ...core.models import BaseRelationModel


class CustomerContact(BaseRelationModel):
    customer = models.ForeignKey("Customer", on_delete=models.CASCADE)
    contact = models.ForeignKey("Contact", on_delete=models.PROTECT)
    is_basic = models.BooleanField(
        default=False
    )  # if True, will show in the list of Owners for select direct owners

    class Meta:
        permissions = [
            ("manage_customercontact", "All permissions for customer contact"),
        ]

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
    forest = models.ForeignKey("Forest", on_delete=models.PROTECT)
    customer = models.ForeignKey("Customer", on_delete=models.CASCADE)

    class Meta:
        permissions = [
            ("manage_forestcustomer", "All permissions for forest customer"),
        ]


class ForestCustomerContact(BaseRelationModel):
    forestcustomer = models.ForeignKey("ForestCustomer", on_delete=models.CASCADE)
    customercontact = models.ForeignKey("CustomerContact", on_delete=models.CASCADE)


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
    user = models.ForeignKey("users.User", on_delete=models.PROTECT)
