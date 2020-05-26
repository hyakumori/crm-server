import logging

from django.utils.translation import gettext as _
from rest_framework.decorators import permission_classes, api_view
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from .exceptions import (
    ContentTypeNotFound,
    ObjectNotFound,
    TagFieldNotExists,
    DuplicatedTagSetting,
)
from .serilalizers import TagSettingSerializer
from .services import TagService
from .schemas import (
    TagSettingInput,
    AssignTagInput,
    TagDeleteInput,
    TagKeyMigrateInput,
    TagKeyMigrateAllInput,
)
from ..activity.services import ActivityService
from ..api.decorators import api_validate_model
from ..core.utils import make_success_json, make_error_json
from ..permissions import IsAdminUser
from ..permissions.services import PermissionService


logger = logging.getLogger(__name__)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_settings_for_type(request, app_name, object_type):
    """
    Return tag setting for object type, mostly will be used to support rendering
    :param request:
    :param app_name:
    :param object_type:
    :return:
    """
    if not app_name or not object_type:
        return make_error_json(_("Wrong parameters"))

    results = TagService.get_setting_for_type(app_name, object_type)
    if not results:
        return make_success_json(data=dict(results=[]))

    return make_success_json(
        data=dict(results=TagSettingSerializer(results, many=True).data)
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_tags_for_type(request, app_name, object_type):
    """
    Return all tags and tags values of an object type
    :param request:
    :param app_name:
    :param object_type:
    :return:
    """
    if not app_name or not object_type:
        return make_error_json(_("Wrong parameters"))

    results = TagService.get_tags_for_type(app_name, object_type)

    return make_success_json(data=dict(results=results))


@api_view(["POST", "PUT", "DELETE"])
@permission_classes([IsAdminUser])
@api_validate_model(TagSettingInput, "tag_setting_input")
def modify_tag_for_type(
    request, app_name, object_type, tag_setting_input, *args, **kwargs
):
    if not app_name or not object_type:
        return make_error_json(_("Wrong parameters"))
    try:
        if request.method == "POST":
            results = TagService.create_tag_setting_for_type(
                app_name, object_type, request.user, tag_setting_input
            )
            return make_success_json(
                data=dict(results=TagSettingSerializer(results).data)
            )
        elif request.method == "PUT":
            results = TagService.update_tag_settings(
                tag_setting_input.id, tag_setting_input
            )
            return make_success_json(
                data=dict(
                    results=TagSettingSerializer(results.get("tag")).data,
                    migrate_results=results.get("migrate"),
                )
            )
        elif request.method == "DELETE":
            results = TagService.delete_tag_settings(tag_setting_input.id)
            return make_success_json(data=dict(results))
    except (ObjectNotFound, ContentTypeNotFound, DuplicatedTagSetting) as e:
        return make_error_json(message=str(e))


@api_view(["POST"])
@permission_classes([IsAdminUser])
@api_validate_model(TagDeleteInput, "tag_delete_input")
def delete_tag_for_type(
    request, app_name, object_type, tag_delete_input, *args, **kwargs
):
    if not app_name or not object_type:
        return make_error_json(_("Wrong parameters"))
    try:
        results = TagService.delete_tag_settings(tag_delete_input.id)
        return make_success_json(data=dict(results=TagSettingSerializer(results).data))
    except (ObjectNotFound, ContentTypeNotFound, DuplicatedTagSetting) as e:
        return make_error_json(message=str(e))


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@api_validate_model(AssignTagInput, "tag_input")
def assign_tag_for_object(
    request, app_name, object_type, tag_input: AssignTagInput, *args, **kwargs
):
    if not app_name or not object_type:
        return make_error_json(_("Wrong parameters"))

    if not PermissionService.check_permissions(
        request, request.user, with_permissions=[f"manage_{object_type}"]
    ):
        raise PermissionDenied()

    try:
        instance, has_changed = TagService.assign_tag_for_object(
            app_name, object_type, request.user, tag_input
        )
        if has_changed:
            ActivityService.log(
                instance.actions.tags_updated, instance, request=request
            )
        return make_success_json(
            data=dict(object_id=str(instance.id), tags=instance.tags)
        )
    except (TagFieldNotExists, ObjectNotFound, ContentTypeNotFound) as e:
        return make_error_json(message=str(e))


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@api_validate_model(TagKeyMigrateInput, "migrate_input")
def migrate_tag_key_objects(
    request, app_name, object_type, migrate_input: TagKeyMigrateInput, *args, **kwargs
):
    if not app_name or not object_type:
        return make_error_json(_("Wrong parameters"))

    if not PermissionService.check_permissions(
        request, request.user, with_permissions=[f"manage_{object_type}"]
    ):
        raise PermissionDenied()

    try:
        if migrate_input.do_update is True:
            logger.warning(
                f"Request on migrating tag key objects {migrate_input.json()}"
            )
        result = TagService.migrate_tag_key_objects(
            app_name, object_type, migrate_input, do_update=migrate_input.do_update
        )
        return make_success_json(data=dict(success=result[0], total=result[1]))
    except (TagFieldNotExists, ObjectNotFound, ContentTypeNotFound) as e:
        return make_error_json(message=str(e))


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@api_validate_model(TagKeyMigrateAllInput, "migrate_input")
def migrate_tag_key_all_objects(
    request,
    app_name,
    object_type,
    migrate_input: TagKeyMigrateAllInput,
    *args,
    **kwargs,
):
    if not app_name or not object_type:
        return make_error_json(_("Wrong parameters"))

    if not PermissionService.check_permissions(
        request, request.user, with_permissions=[f"manage_{object_type}"]
    ):
        raise PermissionDenied()

    try:
        if migrate_input.do_update is True:
            logger.warning(
                f"Request on migrating tag key objects {migrate_input.json()}"
            )
        result = TagService.migrate_tag_key_all_objects(
            app_name, object_type, migrate_input, do_update=migrate_input.do_update
        )
        return make_success_json(data=dict(success=result[0], total=result[1]))
    except (TagFieldNotExists, ObjectNotFound, ContentTypeNotFound) as e:
        return make_error_json(message=str(e))
