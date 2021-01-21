import os

from rest_framework_simplejwt import authentication as jwt_auth
from rest_framework import authentication
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from rest_framework.request import Request
from revproxy.response import get_django_response
from revproxy.views import ProxyView
from base64 import b64encode

geoserver_user = os.getenv("GEOSERVER_USER")
geoserver_pass = os.getenv("GEOSERVER_PASS")

credentials = f"{geoserver_user}:{geoserver_pass}"
credentials_encoded = b64encode(credentials.encode("utf-8")).decode("utf-8")


def initialize_request(request):
    """
    Returns the initial request object.
    """
    # todo: get authenticators from setting file
    return Request(
        request,
        authenticators=[jwt_auth.JWTAuthentication(), authentication.SessionAuthentication(),
                        authentication.TokenAuthentication()]
    )


class CustomProxyView(ProxyView):
    upstream = 'http://geoserver:8080/geoserver/'

    def dispatch(self, request, path):
        self.request = initialize_request(request)
        self.request_headers = self.get_request_headers()

        redirect_to = self._format_path_to_redirect(request)
        if redirect_to:
            return redirect(redirect_to)

        proxy_response = self._created_proxy_response(request, path)

        self._replace_host_on_redirect_location(request, proxy_response)
        self._set_content_type(request, proxy_response)

        response = get_django_response(proxy_response,
                                       strict_cookies=self.strict_cookies)

        self.log.debug("RESPONSE RETURNED: %s", response)
        return response

    def get_request_headers(self):
        if not hasattr(self.request, 'user') or not self.request.user.has_perms(["crm.view_forest"]):
            raise PermissionDenied()
        headers = super(CustomProxyView, self).get_request_headers()
        headers["Authorization"] = f"Basic {credentials_encoded}"
        return headers
