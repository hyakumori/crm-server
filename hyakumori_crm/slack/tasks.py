import asyncio

import httpx
import pytz
from django.conf import settings
from slack import WebClient

from .models import Oauth


def notify(message, user_fullname, dt, obj_title, obj_name):
    slack_client = WebClient(run_async=True)
    accs = list(Oauth.objects.all().values("id", "access_token"))

    async def send_messages():
        async with httpx.AsyncClient() as client:
            for webhook in accs:
                text = f"""
----------------------------------------
{obj_title}: {obj_name}
更新内容: {message}
更新日: {dt.astimezone(pytz.timezone(settings.TIME_ZONE_PRIMARY)).strftime('%Y-%m-%d %H:%M:%S')}
更新者: {user_fullname}
----------------------------------------
"""
                channels_resp = await slack_client.users_conversations(
                    token=webhook["access_token"]
                )
                if channels_resp["ok"] is False:
                    return
                channels = list(map(lambda c: c["id"], channels_resp["channels"]))
                for channel in channels:
                    await slack_client.chat_postMessage(
                        token=webhook["access_token"], channel=channel, text=text
                    )

    asyncio.run(send_messages())


def notify_for_batch(message, user_fullname, dt, obj_title, obj_names):
    slack_client = WebClient(run_async=True)
    accs = list(Oauth.objects.all().values("id", "access_token"))

    async def send_messages():
        async with httpx.AsyncClient() as client:
            for webhook in accs:
                text = f"""
----------------------------------------
{obj_title}: 添付ファイルを参照
更新内容: {message}
更新日: {dt.astimezone(pytz.timezone(settings.TIME_ZONE_PRIMARY)).strftime('%Y-%m-%d %H:%M:%S')}
更新者: {user_fullname}
----------------------------------------
"""
                channels_resp = await slack_client.users_conversations(
                    token=webhook["access_token"]
                )
                if channels_resp["ok"] is False:
                    return
                channels = list(map(lambda c: c["id"], channels_resp["channels"]))
                if channels:
                    await slack_client.files_upload(
                        channels=",".join(channels),
                        token=webhook["access_token"],
                        content="\n".join(obj_names),
                        filename=f"{obj_title}.txt",
                        name=f"{obj_title}.txt",
                        initial_comment=text,
                    )

    asyncio.run(send_messages())
