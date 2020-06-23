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
from ..activity.services import ActivityService, PostalHistoryActions
from ..api.decorators import api_validate_model, get_or_404
from ..core.utils import default_paginator, make_error_json
from ..crm.models import PostalHistory, Attachment
from ..crm.restful.paginations import ListingPagination
from ..crm.restful.serializers import (
    AttachmentSerializer,
    ForestListingSerializer,
    CustomerContactSerializer,
)
from ..users.models import User
from ..users.serializers import UserSerializer
from ..permissions.enums import SystemGroups

from .schemas import (
    PostalHistoryFilter,
    PostalHistoryInput,
    PostalHistoryCustomerInput,
    PostalHistoryListingSerializer,
    PostalHistorySerializer,
)
from .service import (
    add_related_forest,
    add_related_user,
    create_postal_history,
    create_attachment,
    delete_attachment_file,
    add_participants,
    delete_related_forest,
    delete_related_user,
    edit_postal_history,
    get_all_attachments_by_postal_history_pk,
    get_postal_history_by_pk,
    get_attachment_by_pk,
    get_filtered_postal_history_queryset,
    get_participants,
    get_related_forests,
    update_postal_history_tag,
    get_postal_histories_tag_by_ids,
    update_postal_history_other_participants,
)


def postal_history_obj_permission(f):
    def wrapper(*args, **kwargs):
        request = args[0]
        postal_history = kwargs["postal_history"]
        if (
            request.method != "GET"
            and request.user.member_of(SystemGroups.GROUP_LIMITED_USER)
            and postal_history
            and request.user.id != postal_history.author_id
        ):
            raise PermissionDenied()
        return f(*args, **kwargs)

    return wrapper


@api_view(["GET", "POST"])
@permission_classes([PostalHistory.model_perm_cls()])
@api_validate_model(PostalHistoryInput)
def postal_histories(request, data: PostalHistoryInput = None):
    if request.method == "GET":
        paginator_listing = ListingPagination()
        qs = get_filtered_postal_history_queryset(
            PostalHistoryFilter(**request.GET.dict()), request.user
        )
        paged_list = paginator_listing.paginate_queryset(
            request=request, queryset=qs.order_by("-created_at")
        )
        return paginator_listing.get_paginated_response(
            PostalHistoryListingSerializer(paged_list, many=True).data
        )
    else:
        author = request.user
        ph = create_postal_history(author, data)
        ActivityService.log(PostalHistoryActions.created, ph, request=request)
        return Response(data=PostalHistorySerializer(ph).data)


@api_view(["GET"])
@permission_classes([PostalHistory.model_perm_cls()])
def postal_history_headers(request):
    headers = [
        {"value": "id", "text": "", "width": 28},
        {
            "value": "archive_date",
            "text": "書類送付日",
            "sortable": False,
            "align": "center",
        },
        {"value": "title", "text": "表題", "sortable": False, "align": "center"},
        {"value": "content", "text": "書類送付内容", "sortable": False, "align": "center"},
        {"value": "author", "text": "作成者", "sortable": False, "align": "center"},
        {
            "value": "their_participants",
            "text": "送付先",
            "sortable": False,
            "align": "center",
        },
        {
            "value": "our_participants",
            "text": "送付者",
            "sortable": False,
            "align": "center",
        },
        {
            "value": "associated_forest",
            "text": "関連する森",
            "sortable": False,
            "align": "center",
        },
        {"value": "tags", "text": "タグ", "sortable": False, "align": "center"},
    ]
    return Response({"data": headers})


@api_view(["GET", "PUT", "PATCH"])
@permission_classes([PostalHistory.model_perm_cls()])
@get_or_404(
    get_postal_history_by_pk,
    to_name="postal_history",
    pass_to=["kwargs", "request"],
    remove=True,
)
@api_validate_model(PostalHistoryInput)
@postal_history_obj_permission
def postal_history(
    request, *, postal_history: PostalHistory = None, data: PostalHistoryInput = None
):
    if request.method == "GET":
        return Response({"data": PostalHistorySerializer(postal_history).data})
    else:
        updated_postal_history = edit_postal_history(postal_history, data)
        ActivityService.log(
            PostalHistoryActions.basic_info_updated, postal_history, request=request
        )
        return Response({"data": PostalHistorySerializer(updated_postal_history).data})


@api_view(["GET", "POST"])
@permission_classes([PostalHistory.model_perm_cls()])
@parser_classes([MultiPartParser])
@get_or_404(
    get_postal_history_by_pk, to_name="postal_history", pass_to=["kwargs"], remove=True
)
@postal_history_obj_permission
def attachments(request, postal_history: PostalHistory = None):
    # get list attachments
    if request.method == "GET":
        attachments = get_all_attachments_by_postal_history_pk(postal_history.id)
        return Response({"data": AttachmentSerializer(attachments, many=True).data})
    else:
        try:
            new_attachment = create_attachment(postal_history, request)
            ActivityService.log(
                PostalHistoryActions.materials_updated, postal_history, request=request
            )
            return Response(
                {"data": AttachmentSerializer(new_attachment, many=True).data}
            )
        except ValidationError as error:
            return make_error_json(str(error))


@api_view(["GET"])
@permission_classes([PostalHistory.model_perm_cls()])
@get_or_404(
    get_postal_history_by_pk, to_name="postal_history", pass_to=["kwargs"], remove=True
)
@get_or_404(get_attachment_by_pk, to_name="attachment", pass_to=["kwargs"], remove=True)
@postal_history_obj_permission
def attachment_download(
    request, postal_history: PostalHistory = None, attachment: Attachment = None
):
    try:
        encrypt_data = dict(
            postal_history_pk=postal_history.pk,
            attachment_pk=attachment.pk,
            expired=now() + timedelta(minutes=60),
        )
        download_code = encrypt_string(encrypt_data)
        download_url = f"/postal-histories/attachment/{download_code}"
        return Response({"url": download_url, "filename": attachment.filename})
    except EncryptError:
        return make_error_json(message=_("Could not get download url"))


@api_view(["DELETE"])
@permission_classes([PostalHistory.model_perm_cls()])
@get_or_404(
    get_postal_history_by_pk, to_name="postal_history", pass_to=["kwargs"], remove=True
)
@get_or_404(get_attachment_by_pk, to_name="attachment", pass_to=["kwargs"], remove=True)
@postal_history_obj_permission
def attachment(
    request, postal_history: PostalHistory = None, attachment: Attachment = None
):
    is_deleted = delete_attachment_file(postal_history, attachment)
    if is_deleted:
        ActivityService.log(
            PostalHistoryActions.materials_updated, postal_history, request=request
        )
        return Response({"msg": "OK"})
    else:
        raise Http404()


@api_view(["GET", "POST", "DELETE"])
@permission_classes([PostalHistory.model_perm_cls()])
@get_or_404(
    get_postal_history_by_pk, pass_to=["kwargs"], to_name="postal_history", remove=True
)
@postal_history_obj_permission
def postal_history_forests(request, postal_history: PostalHistory = None):
    if request.method == "GET":
        forests = get_related_forests(postal_history)
        return Response({"data": ForestListingSerializer(forests, many=True).data})
    elif request.method == "POST":
        forests = add_related_forest(postal_history, request.data)
        ActivityService.log(
            PostalHistoryActions.forest_list_updated, postal_history, request=request
        )
        return Response({"data": ForestListingSerializer(forests, many=True).data})
    else:
        try:
            is_deleted = delete_related_forest(postal_history, request.data)
            if is_deleted:
                ActivityService.log(
                    PostalHistoryActions.forest_list_updated,
                    postal_history,
                    request=request,
                )
                return Response({"msg": "OK"})
            else:
                raise Http404()
        except ValueError:
            raise Http404()


@api_view(["GET", "PUT"])
@permission_classes([PostalHistory.model_perm_cls()])
@get_or_404(
    get_postal_history_by_pk,
    pass_to=["kwargs", "request"],
    to_name="postal_history",
    remove=True,
)
@api_validate_model(PostalHistoryCustomerInput, methods=["PUT"])
@postal_history_obj_permission
def postal_history_customers(
    request,
    postal_history: PostalHistory = None,
    data: PostalHistoryCustomerInput = None,
):
    if request.method == "GET":
        participants = get_participants(postal_history)
        return Response(CustomerContactSerializer(participants, many=True).data)
    elif request.method == "PUT":
        customers = add_participants(postal_history, data)
        ActivityService.log(
            PostalHistoryActions.customer_participants_updated,
            postal_history,
            request=request,
        )
        return Response({"id": data.postal_history.id})


@api_view(["GET", "POST", "DELETE"])
@permission_classes([PostalHistory.model_perm_cls()])
@get_or_404(
    get_postal_history_by_pk, to_name="postal_history", pass_to=["kwargs"], remove=True
)
@postal_history_obj_permission
def postal_history_users(request, postal_history: PostalHistory = None):
    if request.method == "GET":
        paginator = default_paginator()
        paged_list = paginator.paginate_queryset(
            request=request,
            queryset=User.objects.filter(
                postalhistoryuser__postalhistory_id=postal_history.id,
                postalhistoryuser__deleted=None,
            ).prefetch_related("groups"),
        )
        return paginator.get_paginated_response(
            UserSerializer(paged_list, many=True).data
        )
    elif request.method == "POST":
        users = add_related_user(postal_history, request.data)
        ActivityService.log(
            PostalHistoryActions.staff_participants_updated,
            postal_history,
            request=request,
        )
        return Response({"data": UserSerializer(users, many=True).data})
    else:
        is_deleted = delete_related_user(postal_history, request.data)
        if is_deleted:
            ActivityService.log(
                PostalHistoryActions.staff_participants_updated,
                postal_history,
                request=request,
            )
            return Response({"msg": "OK"})
        else:
            raise Http404()


@api_view(["PUT"])
@permission_classes([PostalHistory.model_perm_cls()])
def postal_history_ids(request):
    ids = request.data
    if ids is None or len(ids) == 0:
        return Response({"data": []})
    else:
        postal_history_tags = get_postal_histories_tag_by_ids(ids)
        return JsonResponse(data={"data": postal_history_tags})


@api_view(["PUT"])
@permission_classes([PostalHistory.model_perm_cls()])
@api_validate_model(TagBulkUpdate)
def postal_history_tags(request, data: TagBulkUpdate):
    update_postal_history_tag(data.dict())
    ActivityService.log_for_batch(
        PostalHistoryActions.tags_bulk_updated,
        PostalHistory,
        obj_pks=data.ids,
        request=request,
    )
    return Response({"msg": "OK"})


@api_view(["PUT"])
@permission_classes([PostalHistory.model_perm_cls()])
@get_or_404(
    get_postal_history_by_pk, to_name="postal_history", pass_to=["kwargs"], remove=True
)
def other_participants(request, postal_history: PostalHistory = None):
    other_participants = request.data.get("other_participants", [])
    update_postal_history_other_participants(postal_history, other_participants)
    ActivityService.log(
        PostalHistoryActions.other_staff_participants_updated,
        postal_history,
        request=request,
    )
    return Response({"msg": "OK"})
