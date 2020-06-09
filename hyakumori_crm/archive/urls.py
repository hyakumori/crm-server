from django.urls import path

from .restful import (
    archives,
    archive_ids,
    archive_tags,
    archive,
    archive_users,
    archive_forests,
    archive_customers,
    attachments,
    attachment,
    attachment_download,
    archive_headers,
    other_participants,
)
from .views import download_file

api_urls = [
    path("archives", archives),
    path("archives/ids", archive_ids),
    path("archives/ids/tags", archive_tags),
    path("archives/<uuid:pk>", archive),
    path("archives/<uuid:pk>/users", archive_users),
    path("archives/<uuid:pk>/forests", archive_forests),
    path("archives/<uuid:pk>/customers", archive_customers),
    path("archives/<uuid:pk>/attachments", attachments),
    path("archives/<uuid:pk>/attachments/<uuid:attachment_pk>", attachment),
    path("archives/<uuid:pk>/other-participants", other_participants),
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
