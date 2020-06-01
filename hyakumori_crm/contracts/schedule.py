import arrow
from django.db import IntegrityError
from django_q.models import Schedule
from django_q.tasks import schedule
from django.conf import settings


def setup():
    try:
        if settings.DEBUG:
            schedule("hyakumori_crm.contracts.tasks.update_status_task",
                     name="debug_update_status_task",
                     schedule_type=Schedule.MINUTES, minutes=5,
                     repeats=5)

        schedule("hyakumori_crm.contracts.tasks.update_status_task",
                 schedule_type=Schedule.DAILY,
                 name="daily_update_status_task",
                 next_run=arrow.utcnow().to("Asia/Tokyo").replace(hour=23, minute=30).datetime)
    except IntegrityError:
        print("tasks already existed")
        pass


def remove():
    Schedule.objects.filter(name="daily_update_status_task").delete()
    Schedule.objects.filter(name="debug_update_status_task").delete()
