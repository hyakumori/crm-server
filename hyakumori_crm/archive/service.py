from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from pydantic import ValidationError
from rest_framework.request import Request

from hyakumori_crm.crm.models import Archive, Attachment
from .schemas import ArchiveInput
from ..crm.models.customer import Customer
from ..crm.models.forest import Forest
from ..crm.models.relations import ArchiveForest, ArchiveCustomer, ArchiveUser
from ..customer.service import get_customer_by_pk
from ..forest.service import get_forest_by_pk


def get_archive_by_pk(pk):
    try:
        return Archive.objects.get(pk=pk)
    except(Archive.DoesNotExist, ValidationError):
        raise ValueError("Archive not found")


def get_attachment_by_pk(attachment_pk):
    try:
        return Attachment.objects.get(pk=attachment_pk)
    except Attachment.DoesNotExist:
        raise ValueError(_("Attachment not found"))


def get_all_attachments_by_archive_pk(archive_pk):
    return Attachment.objects.filter(object_id=archive_pk)


def get_attachment(archive_pk, attachment_pk):
    try:
        return Attachment.objects.filter(object_id=archive_pk, id=attachment_pk, deleted=None)
    except(Attachment.DoesNotExist, ValidationError):
        return ValueError(_("Attachment not found"))


def archive_mapping(archive: Archive, data: ArchiveInput):
    archive.title = data.title
    archive.content = data.content
    archive.location = data.location
    archive.future_action = data.future_action


def create_archive(author: AbstractUser, data: ArchiveInput):
    archive = Archive()
    archive_mapping(archive, data)
    archive.archive_date = datetime.now()
    archive.author = author
    archive.save()
    return archive


def edit_archive(archive: Archive, data: ArchiveInput):
    archive_mapping(archive, data)
    archive.archive_date = data.archive_date
    archive.save()
    return archive


def create_attachment(archive: Archive, req: Request):
    files = req.FILES.getlist("file")
    creator = req.user
    attachments = []
    for file in files:
        attachment = Attachment()
        attachment.creator = creator
        attachment.content_object = archive
        attachment.attachment_file = file
        attachment.save()
        attachments.append(attachment)
    return attachments


def delete_attachment_file(archive: Archive, attachment: Attachment):
    try:
        attachment = get_attachment(archive.id, attachment.id)
        attachment.delete()
        return True
    except Attachment.DoesNotExist:
        return False


def get_related_forests(archive: Archive):
    return Forest.objects.filter(archiveforest__archive__id=archive.id, archiveforest__deleted=None)


def is_archive_forest_exist(archive_pk, forest_pk):
    archive_forest = ArchiveForest.objects.filter(archive__id=archive_pk, forest__id=forest_pk, deleted=None)
    return True if len(archive_forest) == 1 else False


def check_empty_list(validation_list: set):
    if validation_list is None or len(validation_list) == 0:
        return False


def add_related_forest(archive: Archive, data: dict):
    forest_id_list = set(data.get("ids"))
    forests = []
    check_empty_list(forest_id_list)
    for forest_id in forest_id_list:
        forest = get_forest_by_pk(forest_id)
        if is_archive_forest_exist(archive.id, forest_id):
            forests.append(forest)
            continue
        else:
            archive_forest = ArchiveForest()
            archive_forest.archive_id = archive.id
            archive_forest.forest_id = forest.id
            archive_forest.save()
            forests.append(forest)
    return forests


def delete_related_forest(archive: Archive, data: dict):
    forest_id_list = set(data.get("ids"))
    check_empty_list(forest_id_list)
    for forest_id in forest_id_list:
        forest = get_forest_by_pk(forest_id)
        if is_archive_forest_exist(archive.id, forest_id):
            archive_forest = ArchiveForest.objects.get(archive_id=archive.id, forest_id=forest.id, deleted=None)
            archive_forest.delete()
        else:
            continue
    return True


def is_archive_customer_exist(archive_pk, customer_pk):
    archive_customer = ArchiveCustomer.objects.filter(archive__id=archive_pk, customer__id=customer_pk, deleted=None)
    return True if len(archive_customer) == 1 else False


def get_related_customer(archive: Archive):
    return Customer.objects.filter(archivecustomer__archive__id=archive.id, archivecustomer__deleted=None)


def add_related_customer(archive: Archive, data: dict):
    customer_id_list = set(data.get("ids"))
    customers = []
    check_empty_list(customer_id_list)
    for customer_id in customer_id_list:
        customer = get_customer_by_pk(customer_id)
        if is_archive_customer_exist(archive.id, customer_id):
            customers.append(customer)
        else:
            archive_customer = ArchiveCustomer()
            archive_customer.archive_id = archive.id
            archive_customer.customer_id = customer.id
            archive_customer.save()
            customers.append(customer)
    return customers


def delete_related_customer(archive: Archive, data: dict):
    customer_id_list = set(data.get("ids"))
    check_empty_list(customer_id_list)
    for customer_id in customer_id_list:
        customer = get_customer_by_pk(customer_id)
        if is_archive_customer_exist(archive.id, customer_id):
            archive_customer = ArchiveCustomer.objects.get(archive_id=archive.id, customer_id=customer.id,
                                                           deleted=None)
            archive_customer.delete()
        else:
            continue
    return True


def is_archive_user_exist(archive_id, user_id):
    archive_user = ArchiveUser.objects.filter(archive__id=archive_id, user__id=user_id, deleted=None)
    return True if len(archive_user) == 1 else False


def add_related_user(archive: Archive, data: dict):
    user_id_list = set(data.get("ids"))
    users = []
    check_empty_list(user_id_list)
    for user_id in user_id_list:
        user = get_user_model().objects.get(pk=user_id)
        if is_archive_user_exist(archive.id, user_id):
            users.append(user)
        else:
            archive_user = ArchiveUser()
            archive_user.archive_id = archive.id
            archive_user.user_id = user.id
            archive_user.save()
            users.append(user)
    return users


def delete_related_user(archive: Archive, data: dict):
    user_id_list = set(data.get("ids"))
    check_empty_list(user_id_list)
    for user_id in user_id_list:
        user = get_user_model().objects.get(pk=user_id)
        if is_archive_user_exist(archive.id, user_id):
            archive_user = ArchiveUser.objects.get(archive_id=archive.id, user_id=user.id, deleted=None)
            archive_user.delete()
        else:
            continue
    return True
