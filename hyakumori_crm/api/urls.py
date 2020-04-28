from django.urls import re_path

from hyakumori_crm.forest.urls import api_urls as forest_api_urls
from hyakumori_crm.customer.urls import api_urls as customer_api_urls
from hyakumori_crm.users.urls import api_urls as user_api_urls
from hyakumori_crm.permissions.urls import api_urls as permission_api_urls
from .views import notfound_view

urlpatterns = (
    forest_api_urls
    + customer_api_urls
    + user_api_urls
    + permission_api_urls
    + [re_path(".*", notfound_view)]
)
