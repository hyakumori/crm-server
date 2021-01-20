import os

from django.core.exceptions import PermissionDenied
from revproxy.views import ProxyView
from base64 import b64encode

geoserver_user = os.getenv("GEOSERVER_USER")
geoserver_pass = os.getenv("GEOSERVER_PASS")

credentials = f"{geoserver_user}:{geoserver_pass}"
credentials_encoded = b64encode(credentials.encode("utf-8")).decode("utf-8")


class CustomProxyView(ProxyView):
    upstream = 'http://geoserver:8080/geoserver/'

    def get_request_headers(self):
        if not hasattr(self.request, 'user') or not self.request.user.has_perm("crm.view_forest"):
            raise PermissionDenied()
        headers = super(CustomProxyView, self).get_request_headers()
        headers["Authorization"] = f"Basic {credentials_encoded}"
        return headers
