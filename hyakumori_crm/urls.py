from django.urls import include, path, re_path
from hyakumori_crm.graphql import view as graphql_view
from hyakumori_crm.static.views import index_view, test_view
from hyakumori_crm.api.urls import view_urls

urlpatterns = [
    path("", include(view_urls)),
    path("api/v1/", include("hyakumori_crm.api.urls")),
    path("check", test_view, name="check"),
    path("graphql", graphql_view, name="graphql"),
    re_path(".*", index_view, name="index"),
]

