from datetime import timedelta

from django.http import Http404
from django.utils.timezone import now
from django.utils.translation import gettext as _
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from hyakumori_crm.crm.common.utils import EncryptError, encrypt_string
from .cache import refresh_single_archive_cache
from .schemas import ArchiveFilter, ArchiveInput, ArchiveCustomerInput
from .service import (
    add_related_forest,
    add_related_user,
    create_archive,
    create_attachment,
    delete_attachment_file,
    add_participants,
    delete_related_customer,
    delete_related_forest,
    delete_related_user,
    edit_archive,
    get_all_attachments_by_archive_pk,
    get_archive_by_pk,
    get_attachment_by_pk,
    get_filtered_archive_queryset,
    get_participants,
    get_related_forests,
)
from ..activity.services import ActivityService, ArchiveActions
from ..api.decorators import action_login_required, api_validate_model, get_or_404
from ..core.utils import default_paginator, make_error_json
from ..crm.models import Archive, Attachment
from ..crm.restful.paginations import ListingPagination
from ..crm.restful.serializers import (
    ArchiveListingSerializer,
    ArchiveSerializer,
    AttachmentSerializer,
    ForestSerializer,
    ContactSerializer,
    ForestListingSerializer,
    CustomerContactSerializer,
)
from ..users.models import User
from ..users.serializers import UserSerializer


@api_view(["GET", "POST"])
@api_validate_model(ArchiveInput)
@action_login_required(with_permissions=["view_archive", "add_archive"])
def archives(request, data: ArchiveInput = None):
    if request.method == "GET":
        paginator_listing = ListingPagination()
        qs = get_filtered_archive_queryset(ArchiveFilter(**request.GET.dict()))
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


@api_view(["POST"])
@get_or_404(
    get_archive_by_pk, to_name="archive", pass_to=["kwargs", "request"], remove=True
)
@action_login_required(with_permissions=["view_archive", "add_archive"])
def reload_cache(request, *, archive: Archive = None):
    refresh_single_archive_cache(archive)
    return Response()


@api_view(["GET", "PUT", "PATCH"])
@api_validate_model(ArchiveInput)
@get_or_404(
    get_archive_by_pk, to_name="archive", pass_to=["kwargs", "request"], remove=True
)
@action_login_required(with_permissions=["view_archive", "change_archive"])
def archive(request, *, archive: Archive = None, data: ArchiveInput = None):
    if request.method == "GET":
        return Response({"data": ArchiveSerializer(archive).data})
    else:
        updated_archive = edit_archive(archive, data)
        ActivityService.log(ArchiveActions.basic_info_updated, archive, request=request)
        return Response({"data": ArchiveSerializer(updated_archive).data})


@api_view(["GET", "POST"])
@parser_classes([MultiPartParser])
@get_or_404(get_archive_by_pk, to_name="archive", pass_to=["kwargs"], remove=True)
@action_login_required(with_permissions=["view_archive", "change_archive"])
def attachments(request, archive: Archive = None):
    # get list attachments
    if request.method == "GET":
        try:
            attachments = get_all_attachments_by_archive_pk(archive.id)
            return Response({"data": AttachmentSerializer(attachments, many=True).data})
        except:
            return Response(dict(data=[]))
    else:
        new_attachment = create_attachment(archive, request)
        ActivityService.log(ArchiveActions.materials_updated, archive, request=request)
        return Response({"data": AttachmentSerializer(new_attachment, many=True).data})


@api_view(["GET"])
@get_or_404(get_archive_by_pk, to_name="archive", pass_to=["kwargs"], remove=True)
@get_or_404(get_attachment_by_pk, to_name="attachment", pass_to=["kwargs"], remove=True)
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
@get_or_404(get_archive_by_pk, to_name="archive", pass_to=["kwargs"], remove=True)
@get_or_404(get_attachment_by_pk, to_name="attachment", pass_to=["kwargs"], remove=True)
@action_login_required(with_permissions=["view_archive"])
def attachment(request, archive: Archive = None, attachment: Attachment = None):
    is_deleted = delete_attachment_file(archive, attachment)
    if is_deleted:
        ActivityService.log(ArchiveActions.materials_updated, archive, request=request)
        return Response({"msg": "OK"})
    else:
        raise Http404()


@api_view(["GET", "POST", "DELETE"])
@get_or_404(get_archive_by_pk, pass_to=["kwargs"], to_name="archive", remove=True)
@action_login_required(with_permissions=["view_archive", "change_archive"])
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
@action_login_required(with_permissions=["view_archive", "change_archive"])
@get_or_404(
    get_archive_by_pk, pass_to=["kwargs", "request"], to_name="archive", remove=True
)
@api_validate_model(ArchiveCustomerInput, methods=["PUT"])
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
@get_or_404(get_archive_by_pk, to_name="archive", pass_to=["kwargs"], remove=True)
@action_login_required(with_permissions=["view_archive", "change_archive"])
def archive_users(request, archive: Archive = None):
    if request.method == "GET":
        paginator = default_paginator()
        paged_list = paginator.paginate_queryset(
            request=request,
            queryset=User.objects.filter(
                archiveuser__archive__id=archive.id, archiveuser__deleted=None
            ),
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
