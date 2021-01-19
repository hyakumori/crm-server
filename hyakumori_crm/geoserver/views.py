import os

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from revproxy.views import ProxyView
from base64 import b64encode

geoserver_user = os.getenv("GEOSERVER_USER")
geoserver_pass = os.getenv("GEOSERVER_PASS")

credentials = f"{geoserver_user}:{geoserver_pass}"
credentials_encoded = b64encode(credentials.encode("utf-8")).decode("utf-8")


class CustomProxyView(APIView, ProxyView):
    permission_classes = [IsAuthenticated]
    upstream = 'http://geoserver:8080/geoserver/'

    def get_request_headers(self):
        headers = super(CustomProxyView, self).get_request_headers()
        headers["Authorization"] = f"Basic {credentials_encoded}"
        return headers
