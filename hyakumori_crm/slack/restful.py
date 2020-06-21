import requests
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from slack import WebClient

from hyakumori_crm.core.permissions import SuperUserOnly

from .models import Oauth


@api_view(["POST"])
def oauth(request):
    user = authenticate(
        email=request.data.get("email"), password=request.data.get("password")
    )
    if not user or (user and not user.is_superuser):
        return Response({"error": "Authentication failed"}, status=400)
    oauth_resp = requests.post(
        "https://slack.com/api/oauth.v2.access",
        data={
            "client_id": settings.SLACK_CLIENT_ID,
            "client_secret": settings.SLACK_CLIENT_SECRET,
            "code": request.data.get("code"),
        },
    )
    resp_data = oauth_resp.json()
    if resp_data["ok"] is False:
        return Response(resp_data, status=400)
    oauth_token = Oauth.objects.update_or_create(
        team_id=resp_data["team"]["id"],
        defaults=dict(
            team_name=resp_data["team"]["name"],
            access_token=resp_data["access_token"],
            incoming_webhook=resp_data.get("incoming_webhook"),
            authed_user_id=resp_data["authed_user"]["id"],
            scope=resp_data["scope"],
            bot_user_id=resp_data["bot_user_id"],
        ),
    )
    return Response({"msg": "OK"}, status=201)


@api_view(["GET"])
@permission_classes([SuperUserOnly])
def list_installs(request):
    return Response(Oauth.objects.all().values("id", "updated_at", "team_name"))


@api_view(["POST"])
@permission_classes([SuperUserOnly])
def revoke(request):
    try:
        oauth_token = Oauth.objects.get(pk=request.data.get("id"))
    except (Oauth.DoesNotExist, ValueError):
        return Response({"errors": {"id": ["Not found"]}}, status=400)
    slack_client = WebClient()
    resp = slack_client.auth_revoke(token=oauth_token.access_token)
    if resp.data["ok"]:
        oauth_token.delete()
        return Response({"msg": "OK"})
    else:
        return Response({"errors": resp.data}, status=424)
