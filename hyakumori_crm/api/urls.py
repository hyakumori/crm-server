from django.urls import re_path, path

from hyakumori_crm.forest.urls import api_urls as forest_api_urls
from hyakumori_crm.customer.urls import api_urls as customer_api_urls
from hyakumori_crm.users.urls import api_urls as user_api_urls
from hyakumori_crm.permissions.urls import api_urls as permission_api_urls
from hyakumori_crm.archive.urls import api_urls as archive_api_urls
from hyakumori_crm.archive.urls import view_urls as archive_view_urls
from hyakumori_crm.activity.urls import api_urls as activity_api_urls
from hyakumori_crm.tags.urls import api_urls as tags_api_urls
from hyakumori_crm.cache.urls import api_urls as cache_api_urls
from hyakumori_crm.contracts.urls import api_urls as contracttype_api_urls
from .views import notfound_view, maintenance_status

urlpatterns = (
    forest_api_urls
    + customer_api_urls
    + user_api_urls
    + permission_api_urls
    + archive_api_urls
    + activity_api_urls
    + tags_api_urls
    + cache_api_urls
    + contracttype_api_urls
    + [path("maintenance/status", maintenance_status), re_path(".*", notfound_view)]
)

view_urls = []
view_urls += archive_view_urls
