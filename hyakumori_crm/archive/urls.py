from django.urls import path

from .restful import *

api_urls = [
    path("archives", archives),
    path("archives/<uuid:pk>", archive),
    path("archives/<uuid:pk>/users", archive_users),
    path("archives/<uuid:pk>/forests", archive_forests),
    path("archives/<uuid:pk>/customers", archive_customers),
    path("archives/<uuid:pk>/attachments", attachments),
    path("archives/<uuid:pk>/attachments/<uuid:attachment_pk>", attachment)
]
