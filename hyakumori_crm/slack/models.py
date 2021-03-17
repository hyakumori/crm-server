from django.db import models
from django.db.models import JSONField
from django.core.serializers.json import DjangoJSONEncoder

from hyakumori_crm.core.models import AttributesMixin, TimestampMixin


class Oauth(TimestampMixin, AttributesMixin, models.Model):
    access_token = models.CharField(max_length=255)
    team_id = models.CharField(max_length=11, db_index=True)
    team_name = models.CharField(max_length=255)
    scope = models.CharField(max_length=255)
    incoming_webhook = JSONField(null=True, encoder=DjangoJSONEncoder)
    bot_user_id = models.CharField(max_length=11)
    authed_user_id = models.CharField(max_length=11)
