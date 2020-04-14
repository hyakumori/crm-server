from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from hyakumori_crm.customer.restful import CustomerViewSets
from hyakumori_crm.forest.restful import ForestViewSets
from hyakumori_crm.graphql import view as graphql_view
from hyakumori_crm.static.views import index_view, test_view
from hyakumori_crm.core.http import notfound_view

router = DefaultRouter()
router.register("customers", CustomerViewSets, basename="customer")
router.register("forests", ForestViewSets, basename="forest")

urlpatterns = [
    path("api/v1/", include(router.urls)),
    path("api/v1/", include('hyakumori_crm.users.urls')),
    path("api/v1/", include('hyakumori_crm.permissions.urls')),
    re_path("api/v1/.*", notfound_view, name="notfound"),
    path("check", test_view, name="check"),
    path("graphql", graphql_view, name="graphql"),
    re_path(".*", index_view, name="index"),
]
