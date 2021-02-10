from django.urls import include, path, re_path

from hyakumori_crm.geoserver.views import GeoserverProxyView
from hyakumori_crm.graphql import view as graphql_view
from hyakumori_crm.api.urls import view_urls

urlpatterns = [
    path("", include(view_urls)),
    path("api/v1/", include("hyakumori_crm.api.urls")),
    path("graphql", graphql_view, name="graphql"),
    re_path(r'^geoserver/(?P<path>.*)$', GeoserverProxyView.as_view()),
]
