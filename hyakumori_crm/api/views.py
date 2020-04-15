from django.http import Http404
from rest_framework.decorators import api_view


@api_view()
def notfound_view(request):
    raise Http404()
