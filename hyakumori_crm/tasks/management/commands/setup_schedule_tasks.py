from django.core.management.base import BaseCommand
from django_q.models import Schedule

from ...schedule import create_schedule
from hyakumori_crm.contracts.schedule import \
    setup as setup_contracts_schedules, \
    remove as remove_contract_schedules


class Command(BaseCommand):
    help = "Setup schedule tasks"

    def add_arguments(self, parser):
        parser.add_argument(
            "--recreate",
            dest="recreate",
            action="store_true",
            help="remove all schedules first then create again",
        )
        parser.add_argument(
            "--no-recreate",
            dest="recreate",
            action="store_false",
            help="no forcing to create tasks again",
        )
        parser.set_defaults(recreate=False)

    def handle(self, *args, **kwargs):
        if kwargs.get("recreate"):
            Schedule.objects.filter(name="do_healthcheck").delete()
            remove_contract_schedules()

        create_schedule(
            func="hyakumori_crm.tasks.healthcheck.do_healthcheck",
            name="do_healthcheck",
            schedule_type=Schedule.MINUTES,
            minutes=1,
        )
        setup_contracts_schedules()
