from django.urls import path

from .restful import *
from .views import download_file

api_urls = [
    path("archives", archives),
    path("archives/<uuid:pk>", archive),
    path("archives/<uuid:pk>/users", archive_users),
    path("archives/<uuid:pk>/forests", archive_forests),
    path("archives/<uuid:pk>/customers", archive_customers),
    path("archives/<uuid:pk>/attachments", attachments),
    path("archives/<uuid:pk>/attachments/<uuid:attachment_pk>", attachment),
    path(
        "archives/<uuid:pk>/attachments/<uuid:attachment_pk>/download",
        attachment_download,
    ),
    path("archives/attachment/<str:code>", download_file),
    path("archives/headers", archive_headers),
]

view_urls = [
    path("archives/attachment/<str:code>", download_file),
]
