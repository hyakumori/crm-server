from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .constants import ArchiveActions, CustomerActions, ForestActions, UserActions
from .models import ActionLog
from .services import ActivityService
from ..core.utils import make_error_json, make_success_json
from ..crm.models.message_template import MessageTemplate
from ..crm.models.customer import Customer
from ..crm.models.forest import Forest
from ..crm.models.archive import Archive


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_for_object(request, lang_code, app_label, object_type, object_id):
    results = ActivityService.get_log_for_object(
        lang_code, app_label, object_type, object_id
    )
    return Response(dict(results=results, count=len(results), next=None, previous=None))
