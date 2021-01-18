import os

from django.urls import include, path, re_path
from revproxy.views import ProxyView

from hyakumori_crm.graphql import view as graphql_view
from hyakumori_crm.static.views import index_view, test_view
from hyakumori_crm.api.urls import view_urls

geoserver_user = os.getenv("GEOSERVER_USER", "")
geoserver_pass = os.getenv("GEOSERVER_PASS", "")

urlpatterns = [
    path("", include(view_urls)),
    path("api/v1/", include("hyakumori_crm.api.urls")),
    path("check", test_view, name="check"),
    path("graphql", graphql_view, name="graphql"),
    re_path(r'^geoserver/(?P<path>.*)$',
            ProxyView.as_view(upstream=f'http://{geoserver_user}:{geoserver_pass}@geoserver:8080/geoserver/')),
    re_path(".*", index_view, name="index"),
]
