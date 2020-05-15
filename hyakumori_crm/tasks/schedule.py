from django.db import IntegrityError
from django_q.tasks import schedule


def create_schedule(func, name, *args, **kwargs):
    try:
        schedule(func, name=name, *args, **kwargs)
    except IntegrityError:
        pass
