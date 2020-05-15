from django.urls import path

from .restful import *

api_urls = [
    path("activity/<str:lang_code>/<str:app_label>/<str:object_type>/<uuid:object_id>", get_for_object),
]
