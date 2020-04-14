from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils.translation import gettext as _


@api_view(["GET", "POST", "PUT", "PATCH", "OPTIONS", "HEAD", "DELETE"])
@permission_classes([AllowAny])
def notfound_view(request):
    return Response(status=status.HTTP_404_NOT_FOUND, data=dict(
        detail=_("Not found"),
    ))
