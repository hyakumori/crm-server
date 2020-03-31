from django.core.exceptions import ValidationError
from .models import Client


def get(pk):
    try:
        return Client.objects.get(pk=pk)
    except (Client.DoesNotExist, ValidationError):
        return None


def create(data):
    client = Client(**data)
    client.save()
    return client


def update(client, data):
    # do update...
    return client
