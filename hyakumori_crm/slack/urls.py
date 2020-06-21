from django.urls import path

from .restful import oauth, list_installs, revoke


api_urls = [
    path("slack/oauth", oauth),
    path("slack/installs", list_installs),
    path("slack/revoke", revoke),
]
