from django.http import Http404
from django.core.cache import cache
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import exception_handler as rest_exception_handler
from ..core.utils import clear_maintain_task_id_cache


@api_view()
def notfound_view(request):
    raise Http404()


@api_view(["GET"])
def maintenance_status(request):
    task_id = cache.get("maintain_task_id")
    return Response({"in_maintain": bool(task_id)})


def exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = rest_exception_handler(exc, context)

    # make sure if any error, we unset maintenance mode
    clear_maintain_task_id_cache()

    return response
