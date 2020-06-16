from django.urls import path

from .restful import (
    postal_histories,
    postal_history_ids,
    postal_history_tags,
    postal_history,
    postal_history_users,
    postal_history_forests,
    postal_history_customers,
    attachments,
    attachment,
    attachment_download,
    postal_history_headers,
    other_participants,
)
from .views import download_file

api_urls = [
    path("postal-histories", postal_histories),
    path("postal-histories/ids", postal_history_ids),
    path("postal-histories/ids/tags", postal_history_tags),
    path("postal-histories/<uuid:pk>", postal_history),
    path("postal-histories/<uuid:pk>/users", postal_history_users),
    path("postal-histories/<uuid:pk>/forests", postal_history_forests),
    path("postal-histories/<uuid:pk>/customers", postal_history_customers),
    path("postal-histories/<uuid:pk>/attachments", attachments),
    path("postal-histories/<uuid:pk>/attachments/<uuid:attachment_pk>", attachment),
    path("postal-histories/<uuid:pk>/other-participants", other_participants),
    path(
        "postal-histories/<uuid:pk>/attachments/<uuid:attachment_pk>/download",
        attachment_download,
    ),
    path("postal-histories/attachment/<str:code>", download_file),
    path("postal-histories/headers", postal_history_headers),
]

view_urls = [
    path("postal-histories/attachment/<str:code>", download_file),
]
