from django.http import Http404
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from .service import *
from ..activity.services import ActivityService, ArchiveActions
from ..api.decorators import (
    api_validate_model,
    get_or_404,
    action_login_required)
from ..core.utils import default_paginator
from ..crm.restful.serializers import *
from ..users.models import User


@api_view(["GET", "POST"])
@api_validate_model(ArchiveInput)
@action_login_required(with_permissions=["view_archive", "add_archive"])
def archives(request, data: ArchiveInput = None):
    if request.method == 'GET':
        paginator = default_paginator()
        paged_list = paginator.paginate_queryset(
            request=request,
            queryset=Archive.objects.all()
        )
        return paginator.get_paginated_response(ArchiveSerializer(paged_list, many=True).data)
    else:
        author = request.user
        archive = create_archive(author, data)
        ActivityService.log(ArchiveActions.created, archive, request=request)
        return Response(data=ArchiveSerializer(archive).data)


@api_view(["GET", "PUT", "PATCH"])
@api_validate_model(ArchiveInput)
@get_or_404(get_archive_by_pk, to_name='archive', pass_to=["kwargs", "request"], remove=True)
@action_login_required(with_permissions=["view_archive", "change_archive"])
def archive(request, *, archive: Archive = None, data: ArchiveInput):
    if request.method == 'GET':
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
    if request.method == 'GET':
        attachments = get_all_attachments_by_archive_pk(archive.id)
        return Response({"data": AttachmentSerializer(attachments, many=True).data})
    else:
        new_attachment = create_attachment(archive, request)
        ActivityService.log(ArchiveActions.materials_updated, archive, request=request)
        return Response({"data": AttachmentSerializer(new_attachment, many=True).data})


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
    if request.method == 'GET':
        forests = get_related_forests(archive)
        return Response({"data": ForestSerializer(forests, many=True).data})
    elif request.method == 'POST':
        forests = add_related_forest(archive, request.data)
        ActivityService.log(ArchiveActions.forest_list_updated, archive, request=request)
        return Response({"data": ForestSerializer(forests, many=True).data})
    else:
        try:
            is_deleted = delete_related_forest(archive, request.data)
            if is_deleted:
                ActivityService.log(ArchiveActions.forest_list_updated, archive, request=request)
                return Response({"msg": "OK"})
            else:
                raise Http404()
        except ValueError:
            raise Http404()


@api_view(["GET", "POST", "DELETE"])
@get_or_404(get_archive_by_pk, pass_to=["kwargs"], to_name="archive", remove=True)
@action_login_required(with_permissions=["view_archive", "change_archive"])
def archive_customers(request, archive: Archive = None):
    if request.method == 'GET':
        customers = get_related_customer(archive)
        return Response({"data": CustomerSerializer(customers, many=True).data})
    elif request.method == 'POST':
        customers = add_related_customer(archive, request.data)
        ActivityService.log(ArchiveActions.customer_participants_updated, archive, request=request)
        return Response({"data": CustomerSerializer(customers, many=True).data})
    else:
        try:
            is_deleted = delete_related_customer(archive, request.data)
            if is_deleted:
                ActivityService.log(ArchiveActions.customer_participants_updated, archive, request=request)
                return Response({"msg": "OK"})
            else:
                raise Http404()
        except ValueError:
            raise Http404()


@api_view(["GET", "POST", "DELETE"])
@get_or_404(get_archive_by_pk, to_name="archive", pass_to=["kwargs"], remove=True)
@action_login_required(with_permissions=["view_archive", "change_archive"])
def archive_users(request, archive: Archive = None):
    if request.method == 'GET':
        paginator = default_paginator()
        paged_list = paginator.paginate_queryset(
            request=request,
            queryset=User.objects.filter(archiveuser__archive__id=archive.id, archiveuser__deleted=None)
        )
        return paginator.get_paginated_response(UserSerializer(paged_list, many=True).data)
    elif request.method == 'POST':
        users = add_related_user(archive, request.data)
        ActivityService.log(ArchiveActions.staff_participants_updated, archive, request=request)
        return Response({"data": UserSerializer(users, many=True).data})
    else:
        is_deleted = delete_related_user(archive, request.data)
        if is_deleted:
            ActivityService.log(ArchiveActions.staff_participants_updated, archive, request=request)
            return Response({"msg": "OK"})
        else:
            raise Http404()
