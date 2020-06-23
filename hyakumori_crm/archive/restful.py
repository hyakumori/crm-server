from datetime import timedelta

from django.core.exceptions import ValidationError
from django.http import Http404, JsonResponse
from django.utils.timezone import now
from django.utils.translation import gettext as _
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from hyakumori_crm.crm.common.utils import EncryptError, encrypt_string
from hyakumori_crm.crm.schemas.tag import TagBulkUpdate
from .schemas import ArchiveFilter, ArchiveInput, ArchiveCustomerInput
from .service import (
    add_related_forest,
    add_related_user,
    create_archive,
    create_attachment,
    delete_attachment_file,
    add_participants,
    delete_related_forest,
    delete_related_user,
    edit_archive,
    get_all_attachments_by_archive_pk,
    get_archive_by_pk,
    get_attachment_by_pk,
    get_filtered_archive_queryset,
    get_participants,
    get_related_forests,
    update_archive_tag,
    get_archives_tag_by_ids,
    update_archive_other_participants,
)
from ..activity.services import ActivityService, ArchiveActions
from ..api.decorators import api_validate_model, get_or_404
from ..core.utils import default_paginator, make_error_json
from ..crm.models import Archive, Attachment
from ..crm.restful.paginations import ListingPagination
from ..crm.restful.serializers import (
    ArchiveListingSerializer,
    ArchiveSerializer,
    AttachmentSerializer,
    ForestListingSerializer,
    CustomerContactSerializer,
)
from ..users.models import User
from ..users.serializers import UserSerializer
from ..permissions.enums import SystemGroups


def archive_obj_permission(f):
    def wrapper(*args, **kwargs):
        request = args[0]
        archive = kwargs["archive"]
        if (
            request.method != "GET"
            and request.user.member_of(SystemGroups.GROUP_LIMITED_USER)
            and archive
            and request.user.id != archive.author_id
        ):
            raise PermissionDenied()
        return f(*args, **kwargs)

    return wrapper


@api_view(["GET", "POST"])
@permission_classes([Archive.model_perm_cls()])
@api_validate_model(ArchiveInput)
def archives(request, data: ArchiveInput = None):
    if request.method == "GET":
        paginator_listing = ListingPagination()
        qs = get_filtered_archive_queryset(
            ArchiveFilter(**request.GET.dict()), request.user
        )
        paged_list = paginator_listing.paginate_queryset(
            request=request, queryset=qs.order_by("-created_at")
        )
        return paginator_listing.get_paginated_response(
            ArchiveListingSerializer(paged_list, many=True).data
        )
    else:
        author = request.user
        archive = create_archive(author, data)
        ActivityService.log(ArchiveActions.created, archive, request=request)
        return Response(data=ArchiveSerializer(archive).data)


@api_view(["GET"])
@permission_classes([Archive.model_perm_cls()])
def archive_headers(request):
    headers = [
        {"value": "id", "text": "", "align": "center", "width": 28},
        {"value": "archive_date", "text": "日付", "sortable": False, "align": "center"},
        {"value": "title", "text": "タイトル", "sortable": False, "align": "center"},
        {"value": "content", "text": "内容", "sortable": False, "align": "center"},
        {"value": "author", "text": "作成者", "sortable": False, "align": "center"},
        {
            "value": "their_participants",
            "text": "先方参加者",
            "sortable": False,
            "align": "center",
        },
        {
            "value": "our_participants",
            "text": "当方参加者",
            "sortable": False,
            "align": "center",
        },
        {
            "value": "associated_forest",
            "text": "関連する森林",
            "sortable": False,
            "align": "center",
        },
        {"value": "tags", "text": "タグ", "sortable": False, "align": "center"},
    ]
    return Response({"data": headers})


@api_view(["GET", "PUT", "PATCH"])
@permission_classes([Archive.model_perm_cls()])
@get_or_404(
    get_archive_by_pk, to_name="archive", pass_to=["kwargs", "request"], remove=True
)
@api_validate_model(ArchiveInput)
@archive_obj_permission
def archive(request, *, archive: Archive = None, data: ArchiveInput = None):
    if request.method == "GET":
        return Response({"data": ArchiveSerializer(archive).data})
    else:
        updated_archive = edit_archive(archive, data)
        ActivityService.log(ArchiveActions.basic_info_updated, archive, request=request)
        return Response({"data": ArchiveSerializer(updated_archive).data})


@api_view(["GET", "POST"])
@permission_classes([Archive.model_perm_cls()])
@parser_classes([MultiPartParser])
@get_or_404(get_archive_by_pk, to_name="archive", pass_to=["kwargs"], remove=True)
@archive_obj_permission
def attachments(request, archive: Archive = None):
    # get list attachments
    if request.method == "GET":
        attachments = get_all_attachments_by_archive_pk(archive.id)
        return Response({"data": AttachmentSerializer(attachments, many=True).data})
    else:
        try:
            new_attachment = create_attachment(archive, request)
            ActivityService.log(
                ArchiveActions.materials_updated, archive, request=request
            )
            return Response(
                {"data": AttachmentSerializer(new_attachment, many=True).data}
            )
        except ValidationError as error:
            return make_error_json(str(error))


@api_view(["GET"])
@permission_classes([Archive.model_perm_cls()])
@get_or_404(get_archive_by_pk, to_name="archive", pass_to=["kwargs"], remove=True)
@get_or_404(get_attachment_by_pk, to_name="attachment", pass_to=["kwargs"], remove=True)
@archive_obj_permission
def attachment_download(
    request, archive: Archive = None, attachment: Attachment = None
):
    try:
        encrypt_data = dict(
            archive_pk=archive.pk,
            attachment_pk=attachment.pk,
            expired=now() + timedelta(minutes=60),
        )
        download_code = encrypt_string(encrypt_data)
        download_url = f"/archives/attachment/{download_code}"
        return Response({"url": download_url, "filename": attachment.filename})
    except EncryptError:
        return make_error_json(message=_("Could not get download url"))


@api_view(["DELETE"])
@permission_classes([Archive.model_perm_cls()])
@get_or_404(get_archive_by_pk, to_name="archive", pass_to=["kwargs"], remove=True)
@get_or_404(get_attachment_by_pk, to_name="attachment", pass_to=["kwargs"], remove=True)
@archive_obj_permission
def attachment(request, archive: Archive = None, attachment: Attachment = None):
    is_deleted = delete_attachment_file(archive, attachment)
    if is_deleted:
        ActivityService.log(ArchiveActions.materials_updated, archive, request=request)
        return Response({"msg": "OK"})
    else:
        raise Http404()


@api_view(["GET", "POST", "DELETE"])
@permission_classes([Archive.model_perm_cls()])
@get_or_404(get_archive_by_pk, pass_to=["kwargs"], to_name="archive", remove=True)
@archive_obj_permission
def archive_forests(request, archive: Archive = None):
    if request.method == "GET":
        forests = get_related_forests(archive)
        return Response({"data": ForestListingSerializer(forests, many=True).data})
    elif request.method == "POST":
        forests = add_related_forest(archive, request.data)
        ActivityService.log(
            ArchiveActions.forest_list_updated, archive, request=request
        )
        return Response({"data": ForestListingSerializer(forests, many=True).data})
    else:
        try:
            is_deleted = delete_related_forest(archive, request.data)
            if is_deleted:
                ActivityService.log(
                    ArchiveActions.forest_list_updated, archive, request=request
                )
                return Response({"msg": "OK"})
            else:
                raise Http404()
        except ValueError:
            raise Http404()


@api_view(["GET", "PUT"])
@permission_classes([Archive.model_perm_cls()])
@get_or_404(
    get_archive_by_pk, pass_to=["kwargs", "request"], to_name="archive", remove=True
)
@api_validate_model(ArchiveCustomerInput, methods=["PUT"])
@archive_obj_permission
def archive_customers(
    request, archive: Archive = None, data: ArchiveCustomerInput = None
):
    if request.method == "GET":
        participants = get_participants(archive)
        return Response(CustomerContactSerializer(participants, many=True).data)
    elif request.method == "PUT":
        customers = add_participants(archive, data)
        ActivityService.log(
            ArchiveActions.customer_participants_updated, archive, request=request
        )
        return Response({"id": data.archive.id})


@api_view(["GET", "POST", "DELETE"])
@permission_classes([Archive.model_perm_cls()])
@get_or_404(get_archive_by_pk, to_name="archive", pass_to=["kwargs"], remove=True)
@archive_obj_permission
def archive_users(request, archive: Archive = None):
    if request.method == "GET":
        paginator = default_paginator()
        paged_list = paginator.paginate_queryset(
            request=request,
            queryset=User.objects.filter(
                archiveuser__archive__id=archive.id, archiveuser__deleted=None
            ).prefetch_related("groups"),
        )
        return paginator.get_paginated_response(
            UserSerializer(paged_list, many=True).data
        )
    elif request.method == "POST":
        users = add_related_user(archive, request.data)
        ActivityService.log(
            ArchiveActions.staff_participants_updated, archive, request=request
        )
        return Response({"data": UserSerializer(users, many=True).data})
    else:
        is_deleted = delete_related_user(archive, request.data)
        if is_deleted:
            ActivityService.log(
                ArchiveActions.staff_participants_updated, archive, request=request
            )
            return Response({"msg": "OK"})
        else:
            raise Http404()


@api_view(["PUT"])
@permission_classes([Archive.model_perm_cls()])
def archive_ids(request):
    ids = request.data
    if ids is None or len(ids) == 0:
        return Response({"data": []})
    else:
        archive_tags = get_archives_tag_by_ids(ids)
        return JsonResponse(data={"data": archive_tags})


@api_view(["PUT"])
@permission_classes([Archive.model_perm_cls()])
@api_validate_model(TagBulkUpdate)
def archive_tags(request, data: TagBulkUpdate):
    update_archive_tag(data.dict())
    ActivityService.log_for_batch(
        ArchiveActions.tags_bulk_updated, Archive, obj_pks=data.ids, request=request
    )
    return Response({"msg": "OK"})


@api_view(["PUT"])
@permission_classes([Archive.model_perm_cls()])
@get_or_404(get_archive_by_pk, to_name="archive", pass_to=["kwargs"], remove=True)
def other_participants(request, archive: Archive = None):
    other_participants = request.data.get("other_participants", [])
    update_archive_other_participants(archive, other_participants)
    ActivityService.log(
        ArchiveActions.other_staff_participants_updated, archive, request=request
    )
    return Response({"msg": "OK"})
