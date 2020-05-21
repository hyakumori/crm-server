from django_q.tasks import async_task
from rest_framework.decorators import api_view
from hyakumori_crm.api.decorators import action_login_required, get_or_404
from hyakumori_crm.archive.service import get_archive_by_pk
from hyakumori_crm.cache.archive import refresh_single_archive_cache
from hyakumori_crm.cache.forest import refresh_customer_forest_cache
from hyakumori_crm.core.utils import make_success_json
from hyakumori_crm.crm.models import Archive


@api_view(["POST"])
@get_or_404(
    get_archive_by_pk, to_name="archive", pass_to=["kwargs", "request"], remove=True
)
@action_login_required(with_permissions=["manage_archive"])
def reload_single_archive_cache(request, *, archive: Archive = None):
    async_task(refresh_single_archive_cache, archive)
    return make_success_json(data=dict(message="done"))


@api_view(["POST"])
@action_login_required(with_permissions=["change_forest"])
def reload_forest_cache(request):
    forest_ids = request.data.get("forest_ids", [])
    async_task(refresh_customer_forest_cache, forest_ids)
    return make_success_json(data=dict(msg="done"))
