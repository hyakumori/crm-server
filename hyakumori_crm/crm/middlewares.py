import os.path
from django.http import HttpResponse, JsonResponse
from django.db.models import F
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from django_q.models import Task
from django.core.cache import cache


class ServiceUnavailable(APIException):
    status_code = 503
    default_detail = "Service temporarily unavailable, try again later."
    default_code = "service_unavailable"


def in_maintain_middleware(get_response):
    def middleware(request):
        if request.path.startswith("/api/v1") and request.method not in [
            "GET",
            "OPTIONS",
        ]:
            if cache.get("maintain_task_id") is not None:
                return JsonResponse({"detail": "Service Unavailable"}, status=503)
        resp = get_response(request)

        return resp

    return middleware
