import itertools
import operator
from functools import reduce
from urllib import parse

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError as DjValidationError
from django.db import connection
from django.db.models import F, Subquery, OuterRef, Count, Q, CharField, Value as V
from django.db.models.functions import Concat
from django.db.models.expressions import RawSQL
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from pydantic import ValidationError
from rest_framework.request import Request

from hyakumori_crm.cache.postal_history import (
    refresh_customers_cache,
    refresh_forest_cache,
    refresh_user_participants_cache,
)
from ..crm.models import (
    PostalHistory,
    Attachment,
    Contact,
    Forest,
    PostalHistoryForest,
    PostalHistoryCustomer,
    PostalHistoryUser,
    PostalHistoryCustomerContact,
    CustomerContact,
)
from ..forest.service import get_forest_by_pk
from ..tags.filters import TagsFilterSet
from ..permissions.enums import SystemGroups

from .schemas import PostalHistoryInput, PostalHistoryFilter, PostalHistoryCustomerInput


def get_postal_history_by_pk(pk):
    try:
        return PostalHistory.objects.get(pk=pk)
    except (PostalHistory.DoesNotExist, ValidationError):
        raise ValueError("Postal history not found")


def get_postal_histories_tag_by_ids(ids: list):
    with connection.cursor() as cursor:
        cursor.execute(
            """
select distinct jsonb_object_keys(tags)
from crm_postalhistory
where id in %(ids)s""",
            {"ids": tuple(ids)},
        )
        tags = cursor.fetchall()
    return list(itertools.chain(*tags))


def get_attachment_by_pk(attachment_pk):
    try:
        return Attachment.objects.get(pk=attachment_pk)
    except Attachment.DoesNotExist:
        raise ValueError(_("Attachment not found"))


def get_all_attachments_by_postal_history_pk(postal_history_pk):
    return Attachment.objects.filter(object_id=postal_history_pk)


def get_attachment(postal_history_pk, attachment_pk):
    try:
        return Attachment.objects.filter(
            object_id=postal_history_pk, id=attachment_pk, deleted=None
        )
    except (Attachment.DoesNotExist, ValidationError):
        return ValueError(_("Attachment not found"))


def postal_history_mapping(postal_history: PostalHistory, data: PostalHistoryInput):
    postal_history.title = data.title
    postal_history.archive_date = data.archive_date
    postal_history.content = data.content


def create_postal_history(author: AbstractUser, data: PostalHistoryInput):
    postal_history = PostalHistory()
    postal_history_mapping(postal_history, data)
    postal_history.author = author
    postal_history.save()
    return postal_history


def edit_postal_history(postal_history: PostalHistory, data: PostalHistoryInput):
    postal_history_mapping(postal_history, data)
    postal_history.save()
    return postal_history


def check_valid_file_extension(files):
    valid_extensions = [
        "xlsx",
        "xls",
        "csv",
        "doc",
        "docx",
        "pdf",
        "zip",
        "png",
        "jpg",
        "gif",
        "bmp",
        "tif",
        "txt",
    ]
    valid_files = []
    for file in files:
        file_extension = parse.unquote(file.name).split(".")[-1]
        if file_extension.lower() in valid_extensions:
            valid_files.append(file)
        else:
            raise DjValidationError("Unsupported file extension")
    return valid_files


def create_attachment(postal_history: PostalHistory, req: Request):
    files = req.FILES.getlist("file")
    try:
        valid_files = check_valid_file_extension(files)
        creator = req.user
        attachments = []
        for file in valid_files:
            attachment = Attachment()
            attachment.creator = creator
            attachment.content_object = postal_history
            attachment.attachment_file = file
            attachment.attributes["original_file_name"] = parse.unquote(file.name)
            attachment.attributes["content_type"] = file.content_type
            attachment.attributes["original_file_size"] = file.size
            attachment.save()
            attachments.append(attachment)
        return attachments
    except ValidationError as error:
        return ValueError(_(error))


def delete_attachment_file(postal_history: PostalHistory, attachment: Attachment):
    try:
        attachment = get_attachment(postal_history.id, attachment.id)
        attachment.delete()
        return True
    except Attachment.DoesNotExist:
        return False


def get_related_forests(postal_history: PostalHistory):
    return Forest.objects.filter(
        postalhistoryforest__postalhistory_id=postal_history.id,
        postalhistoryforest__deleted=None,
    )


def is_postal_history_forest_exist(postal_history_pk, forest_pk):
    postal_history_forest = PostalHistoryForest.objects.filter(
        postalhistory__id=postal_history_pk, forest__id=forest_pk, deleted=None
    )
    return True if len(postal_history_forest) == 1 else False


def check_empty_list(validation_list: set):
    if validation_list is None or len(validation_list) == 0:
        return False


def add_related_forest(postal_history: PostalHistory, data: dict):
    forest_id_list = set(data.get("ids"))
    forests = []
    check_empty_list(forest_id_list)
    for forest_id in forest_id_list:
        forest = get_forest_by_pk(forest_id)
        if is_postal_history_forest_exist(postal_history.id, forest_id):
            forests.append(forest)
            continue
        else:
            postal_history_forest = PostalHistoryForest()
            postal_history_forest.postalhistory_id = postal_history.id
            postal_history_forest.forest_id = forest.id
            postal_history_forest.save()
            forests.append(forest)
    refresh_forest_cache(postal_history, save=True)
    return forests


def delete_related_forest(postal_history: PostalHistory, data: dict):
    forest_id_list = set(data.get("ids"))
    check_empty_list(forest_id_list)
    for forest_id in forest_id_list:
        forest = get_forest_by_pk(forest_id)
        if is_postal_history_forest_exist(postal_history.id, forest_id):
            postal_history_forest = PostalHistoryForest.objects.get(
                postalhistory_id=postal_history.id, forest_id=forest.id, deleted=None
            )
            postal_history_forest.force_delete()
        else:
            continue
    refresh_forest_cache(postal_history, save=True)
    return True


def is_postal_history_customer_exist(postal_history_pk, customer_pk):
    postal_history_customer = PostalHistoryCustomer.objects.filter(
        postalhistory__id=postal_history_pk, customer__id=customer_pk, deleted=None
    )
    return True if len(postal_history_customer) == 1 else False


def get_participants(postal_history: PostalHistory):
    cc = CustomerContact.objects.filter(is_basic=True, contact=OuterRef("pk"))
    cc_forests_count = cc.values("id", "customer_id").annotate(
        forests_count=Count("customer__forestcustomer")
    )
    cc_business_id = cc.annotate(business_id=F("customer__business_id"))
    return (
        Contact.objects.filter(
            **{
                "customercontact__postalhistorycustomercontact"
                "__postalhistorycustomer__postalhistory_id": postal_history.id
            }
        )
        .annotate(
            customer_id=F(
                "customercontact__postalhistorycustomercontact__postalhistorycustomer__customer_id"  # noqa
            ),
            cc_attrs=F("customercontact__attributes"),
        )
        .annotate(is_basic=F("customercontact__is_basic"))
        .annotate(
            customer_name_kanji=RawSQL(
                """
select C0.name_kanji
from crm_contact C0
join crm_customercontact CC0
on C0.id = CC0.contact_id and CC0.is_basic = true
where CC0.customer_id = crm_customercontact.customer_id""",
                params=[],
            )
        )
        .annotate(forests_count=Subquery(cc_forests_count.values("forests_count")[:1]))
        .annotate(business_id=Subquery(cc_business_id.values("business_id")[:1]))
    )


def add_participants(postal_history: PostalHistory, data: PostalHistoryCustomerInput):
    accs = []
    for item in data.added:
        cc = CustomerContact.objects.get(
            customer_id=item.customer_id, contact_id=item.contact_id
        )
        ac, _ = PostalHistoryCustomer.objects.get_or_create(
            postalhistory_id=postal_history.id, customer_id=item.customer_id
        )
        acc = PostalHistoryCustomerContact(
            postalhistorycustomer_id=ac.id, customercontact_id=cc.id
        )
        accs.append(acc)
    PostalHistoryCustomerContact.objects.bulk_create(accs)

    for item in data.deleted:
        cc = CustomerContact.objects.get(
            customer_id=item.customer_id, contact_id=item.contact_id
        )
        ac = (
            PostalHistoryCustomer.objects.filter(
                postalhistory_id=postal_history.id, customer_id=item.customer_id
            )
            .prefetch_related("postalhistorycustomercontact_set")
            .first()
        )
        cc.postalhistorycustomercontact_set.filter(
            customercontact_id=cc.id, postalhistorycustomer_id=ac.id
        ).delete()

        ac.refresh_from_db()

        if ac.postalhistorycustomercontact_set.count() == 0:
            ac.force_delete()

    postal_history.save(update_fields=["updated_at"])
    refresh_customers_cache(postal_history, save=True)
    return postal_history


def is_postal_history_user_exist(postalhistory_id, user_id):
    postal_history_user = PostalHistoryUser.objects.filter(
        postalhistory__id=postalhistory_id, user__id=user_id, deleted=None
    )
    return True if len(postal_history_user) == 1 else False


def add_related_user(postal_history: PostalHistory, data: dict):
    user_id_list = set(data.get("ids"))
    users = []
    check_empty_list(user_id_list)
    for user_id in user_id_list:
        user = get_user_model().objects.get(pk=user_id)
        if is_postal_history_user_exist(postal_history.id, user_id):
            users.append(user)
        else:
            postal_history_user = PostalHistoryUser()
            postal_history_user.postalhistory_id = postal_history.id
            postal_history_user.user_id = user.id
            postal_history_user.save()
            users.append(user)
    refresh_user_participants_cache(postal_history, True)
    return users


def delete_related_user(postal_history: PostalHistory, data: dict):
    user_id_list = set(data.get("ids"))
    check_empty_list(user_id_list)
    for user_id in user_id_list:
        user = get_user_model().objects.get(pk=user_id)
        if is_postal_history_user_exist(postal_history.id, user_id):
            postal_history_user = PostalHistoryUser.objects.get(
                postalhistory_id=postal_history.id, user_id=user.id, deleted=None
            )
            postal_history_user.force_delete()
        else:
            continue
    refresh_user_participants_cache(postal_history, True)
    return True


def get_filtered_postal_history_queryset(
    postal_history_filter: PostalHistoryFilter, user
):
    postal_history_filter = postal_history_filter.dict()
    active_filters = dict()
    mapping = {
        "id": "id",
        "archive_date": "archive_date_text",
        "title": "title",
        "author": "author_fullname",
        "content": "content",
        "associated_forest": "attributes__forest_cache__repr",
        "our_participants": "attributes__user_cache__repr",
        "their_participants": "attributes__customer_cache__repr",
        "tags": "tags_repr",
    }
    for k, v in postal_history_filter.items():
        if v is not None:
            active_filters[mapping[k]] = v
    qs = PostalHistory.objects.select_related("author").all()
    if user.member_of(SystemGroups.GROUP_LIMITED_USER):
        qs = qs.distinct().filter(
            Q(author_id=user.id) | Q(postalhistoryuser__user_id=user.id)
        )
    if len(active_filters.keys()) > 0:
        qs = qs.annotate(
            archive_date_text=RawSQL(
                "to_char((archive_date at time zone %s), 'YYYY-MM-DD HH24:MI')",
                [settings.TIME_ZONE_PRIMARY],
            ),
            author_fullname=Concat(
                F("author__last_name"),
                V(" "),
                F("author__first_name"),
                output_field=CharField(),
            ),
        ).select_related("author")
        qs = TagsFilterSet.get_tags_repr_queryset(qs)
        for k, value in active_filters.items():
            values = list(set(map(lambda v: v.strip(), value.split(","))))
            if len(values) == 1 and values[0] == "":
                conditions = Q(**{f"{k}__isnull": True}) | Q(**{f"{k}__exact": None})
            else:
                search_field_filter = k + "__icontains"
                conditions = reduce(
                    operator.or_,
                    (
                        Q(**{search_field_filter: value})
                        for value in values
                        if len(value) > 0
                    ),
                )
            qs = qs.filter(conditions)
    return qs


def update_postal_history_tag(data: dict):
    ids = data.get("ids")
    tag_key = data.get("key")
    new_value = data.get("value")
    PostalHistory.objects.filter(id__in=ids).update(
        tags=RawSQL("tags || jsonb_build_object(%s, %s)", params=[tag_key, new_value])
    )


def update_postal_history_other_participants(postal_history, participants):
    postal_history.attributes.update({"other_participants": participants})
    postal_history.save(update_fields=["attributes", "updated_at"])
    return postal_history
