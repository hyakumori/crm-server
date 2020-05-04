from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .constants import ArchiveActions, CustomerActions, ForestActions, UserActions
from .models import ActionLog
from .services import ActivityService
from ..core.utils import make_success_json
from ..crm.models.message_template import MessageTemplate
from ..crm.models.customer import Customer
from ..crm.models.forest import Forest
from ..crm.models.archive import Archive


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_for_object(request, lang_code, app_label, object_type, object_id):
    results = ActivityService.get_log_for_object(lang_code, app_label, object_type, object_id)
    return Response(dict(results=results, count=len(results), next=None, previous=None))


@api_view(["POST"])
@permission_classes([IsAdminUser])
def setup_templates(request):
    try:
        with transaction.atomic():
            MessageTemplate.objects.all().delete()

            ActivityService.import_message_templates(for_type="forest", action_class=ForestActions)
            ActivityService.import_message_templates(for_type="customer", action_class=CustomerActions)
            ActivityService.import_message_templates(for_type="archive", action_class=ArchiveActions)
            ActivityService.import_message_templates(for_type="user", action_class=UserActions)

            ActionLog.objects\
                .filter(template_name__in=["forest.created", "customer.created", "archive.created", "user.created"])\
                .all().delete()

            admin = get_user_model().objects.filter(is_superuser=True).order_by("date_joined").first()
            for forest in Forest.objects.iterator():
                ActivityService.log(ForestActions.created, forest, user=admin, created_at=forest.created_at)

            for customer in Customer.objects.iterator():
                ActivityService.log(CustomerActions.created, customer, user=admin, created_at=customer.created_at)

            for user in get_user_model().objects.iterator():
                ActivityService.log(UserActions.created, user, user=admin, created_at=user.date_joined)

            return make_success_json(data=dict(success=True))

    except Exception as e:
        return make_success_json(data=dict(success=False, error=str(e)))

