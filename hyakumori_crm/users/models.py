import uuid

from django.contrib.auth.models import AbstractUser, Group
from django.contrib.postgres.fields.jsonb import JSONField
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .managers import UserManager


def default_username():
    return f"u{uuid.uuid4().hex[0:8]}"


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(
        default=default_username, max_length=200, db_index=True, null=True, unique=True
    )
    email = models.EmailField(_("email address"), unique=True, db_index=True)
    profile = JSONField(blank=True, default=dict)
    settings = JSONField(blank=True, default=dict)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name}"

    def member_of(self, group_name):
        return self.groups.filter(name=group_name).exists()
