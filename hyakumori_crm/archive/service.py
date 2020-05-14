from urllib import parse

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db.models import F, Subquery, OuterRef, Count
from django.db.models.expressions import Func, RawSQL, Value
from django.utils.translation import gettext_lazy as _
from pydantic import ValidationError
from rest_framework.request import Request

from ..crm.models import (
    Archive,
    Attachment,
    Customer,
    Contact,
    Forest,
    ArchiveForest,
    ArchiveCustomer,
    ArchiveUser,
    ArchiveCustomerContact,
    CustomerContact,
)
from ..customer.service import get_customer_by_pk
from ..forest.service import get_forest_by_pk

from .cache import (
    refresh_customers_cache,
    refresh_forest_cache,
    refresh_user_participants_cache,
)
from .schemas import ArchiveInput, ArchiveCustomerInput, ArchiveFilter


def get_archive_by_pk(pk):
    try:
        return Archive.objects.get(pk=pk)
    except (Archive.DoesNotExist, ValidationError):
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
        return Attachment.objects.filter(
            object_id=archive_pk, id=attachment_pk, deleted=None
        )
    except (Attachment.DoesNotExist, ValidationError):
        return ValueError(_("Attachment not found"))


def archive_mapping(archive: Archive, data: ArchiveInput):
    archive.title = data.title
    archive.content = data.content
    archive.location = data.location
    archive.archive_date = data.archive_date
    archive.future_action = data.future_action


def create_archive(author: AbstractUser, data: ArchiveInput):
    archive = Archive()
    archive_mapping(archive, data)
    archive.author = author
    archive.save()
    return archive


def edit_archive(archive: Archive, data: ArchiveInput):
    archive_mapping(archive, data)
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
        attachment.attributes["original_file_name"] = parse.unquote(file.name)
        attachment.attributes["content_type"] = file.content_type
        attachment.attributes["original_file_size"] = file.size
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
    return Forest.objects.filter(
        archiveforest__archive__id=archive.id, archiveforest__deleted=None
    )


def is_archive_forest_exist(archive_pk, forest_pk):
    archive_forest = ArchiveForest.objects.filter(
        archive__id=archive_pk, forest__id=forest_pk, deleted=None
    )
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
    refresh_forest_cache(archive, save=True)
    return forests


def delete_related_forest(archive: Archive, data: dict):
    forest_id_list = set(data.get("ids"))
    check_empty_list(forest_id_list)
    for forest_id in forest_id_list:
        forest = get_forest_by_pk(forest_id)
        if is_archive_forest_exist(archive.id, forest_id):
            archive_forest = ArchiveForest.objects.get(
                archive_id=archive.id, forest_id=forest.id, deleted=None
            )
            archive_forest.force_delete()
        else:
            continue
    refresh_forest_cache(archive, save=True)
    return True


def is_archive_customer_exist(archive_pk, customer_pk):
    archive_customer = ArchiveCustomer.objects.filter(
        archive__id=archive_pk, customer__id=customer_pk, deleted=None
    )
    return True if len(archive_customer) == 1 else False


def get_participants(archive: Archive):
    cc = (
        CustomerContact.objects.filter(is_basic=True, contact=OuterRef("pk"))
        .values("id", "customer_id")
        .annotate(forests_count=Count("customer__forestcustomer"))
    )
    return (
        Contact.objects.filter(
            customercontact__archivecustomercontact__archivecustomer__archive_id=archive.id
        )
        .annotate(
            customer_id=F(
                "customercontact__archivecustomercontact__archivecustomer__customer_id"
            ),
            cc_attrs=F("customercontact__attributes")
        )
        .annotate(is_basic=F("customercontact__is_basic"))
        .annotate(
            customer_name_kanji=RawSQL(
                """(select
                        C0.name_kanji
                        from crm_contact C0
                    join crm_customercontact CC0
                        on C0.id = CC0.contact_id and CC0.is_basic = true
                    where CC0.customer_id = crm_customercontact.customer_id)""",
                params=[],
            )
        )
        .annotate(forests_count=Subquery(cc.values("forests_count")[:1]))
    )


def add_participants(archive: Archive, data: ArchiveCustomerInput):
    accs = []
    for item in data.added:
        cc = CustomerContact.objects.get(
            customer_id=item.customer_id, contact_id=item.contact_id
        )
        ac, _ = ArchiveCustomer.objects.get_or_create(
            archive_id=archive.id, customer_id=item.customer_id
        )
        acc = ArchiveCustomerContact(archivecustomer_id=ac.id, customercontact_id=cc.id)
        accs.append(acc)
    ArchiveCustomerContact.objects.bulk_create(accs)

    for item in data.deleted:
        cc = CustomerContact.objects.get(
            customer_id=item.customer_id, contact_id=item.contact_id
        )
        ac = (
            ArchiveCustomer.objects.filter(
                archive_id=archive.id, customer_id=item.customer_id
            )
            .prefetch_related("archivecustomercontact_set")
            .first()
        )
        cc.archivecustomercontact_set.filter(
            customercontact_id=cc.id, archivecustomer_id=ac.id
        ).delete()
        if len(ac.archivecustomercontact_set.all()) == 0:
            ac.force_delete()

    archive.save(update_fields=["updated_at"])
    refresh_customers_cache(archive, save=True)
    return archive


def delete_related_customer(archive: Archive, data: dict):
    customer_id_list = set(data.get("ids"))
    check_empty_list(customer_id_list)
    for customer_id in customer_id_list:
        customer = get_customer_by_pk(customer_id)
        if is_archive_customer_exist(archive.id, customer_id):
            archive_customer = ArchiveCustomer.objects.get(
                archive_id=archive.id, customer_id=customer.id, deleted=None
            )
            archive_customer.force_delete()
        else:
            continue
    refresh_customers_cache(archive, save=True)
    return True


def is_archive_user_exist(archive_id, user_id):
    archive_user = ArchiveUser.objects.filter(
        archive__id=archive_id, user__id=user_id, deleted=None
    )
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
    refresh_user_participants_cache(archive, True)
    return users


def delete_related_user(archive: Archive, data: dict):
    user_id_list = set(data.get("ids"))
    check_empty_list(user_id_list)
    for user_id in user_id_list:
        user = get_user_model().objects.get(pk=user_id)
        if is_archive_user_exist(archive.id, user_id):
            archive_user = ArchiveUser.objects.get(
                archive_id=archive.id, user_id=user.id, deleted=None
            )
            archive_user.force_delete()
        else:
            continue
    refresh_user_participants_cache(archive, True)
    return True


def get_filtered_archive_queryset(archive_filter: ArchiveFilter):
    try:
        archive_filter = archive_filter.dict()
        active_filters = dict()
        mapping = {
            "id": "id__icontains",
            "content": "content__icontains",
            "archive_date": "archive_date_text__icontains",
            "location": "location__icontains",
            "title": "title__icontains",
            "future_action": "future_action__icontains",
            "author": "attributes__user_cache__repr__icontains",
            "associated_forest": "attributes__forest_cache__repr__icontains",
            "our_participants": "attributes__user_cache__repr__icontains",
            "their_participants": "attributes__customer_cache__repr__icontains",
        }

        for k, v in archive_filter.items():
            if v is not None:
                active_filters[mapping[k]] = v

        if len(active_filters.keys()) > 0:
            return Archive.objects.annotate(
                archive_date_text=Func(
                    F("archive_date"), Value("YYYY-MM-DD HH24:MI"), function="to_char"
                )
            ).select_related("author").filter(**active_filters)

        return Archive.objects.select_related("author").all()
    except Exception as e:
        return Archive.objects.none()


def _archives_list_raw_sql(page_size, page, filters, order_by):
    limit = page_size
    offset = page * page_size
    active_fields = [
        "forests",
        "participants",
        "customers",
        "title",
        "location",
        "content",
        "future_action",
    ]
    query = """
        select id,
               author,
               forests,
               participants,
               customers,
               title,
               location,
               content,
               future_action,
               archive_date,
               attributes
        from (
             select crm_archive.id,
                    crm_archive.title         as                                                       title,
                    crm_archive.location      as                                                       location,
                    crm_archive.content       as                                                       content,
                    crm_archive.future_action as                                                       future_action,
                    crm_archive.archive_date  as                                                       archive_date,
                    crm_archive.attributes    as                                                       attributes,
                    array_to_string(array_agg(DISTINCT (uu.last_name || ' ' || uu.first_name)), ',')   author,
                    array_to_string(array_agg(DISTINCT f.internal_id), ',')                            forests,
                    array_to_string(array_agg(DISTINCT (auu.last_name || ' ' || auu.first_name)), ',') participants,
                    array_to_string(
                            array_agg(
                                DISTINCT (cc.name_kanji ->> 'last_name') || ' ' || (cc.name_kanji ->> 'first_name')),
                            ',')                                                                       customers
             from crm_archive
                      left join crm_archiveforest af on crm_archive.id = af.archive_id
                      left join crm_forest f on af.forest_id = f.id
                      left join crm_archivecustomer ac on crm_archive.id = ac.archive_id
                      left join crm_customer cc on ac.customer_id = cc.id
                      left join crm_archiveuser au on crm_archive.id = au.archive_id
                      left join users_user auu on au.user_id = auu.id
                      left join users_user uu on crm_archive.author_id = uu.id
             where au.deleted is null
               and ac.deleted is null
               and af.deleted is null
             group by crm_archive.id
        ) results
        -- where participants ilike '%user%'
        -- limit 25
        -- offset 0
    """
    return query
