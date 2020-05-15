from distutils.util import strtobool

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from hyakumori_crm.permissions.services import PermissionService
from hyakumori_crm.activity.services import ActivityService
from hyakumori_crm.tags.services import TagService


class Command(BaseCommand):
    help = "Doing system setup"

    def add_arguments(self, parser):
        parser.add_argument(
            "--sync-created",
            dest="sync_created",
            action="store_true",
            help="create all `created` logs, require some time to finish",
        )
        parser.add_argument(
            "--no-sync-created",
            dest="sync_created",
            action="store_false",
            help="disable insert `created` logs",
        )
        parser.set_defaults(sync_created=False)

    def handle(self, *args, **kwargs):
        try:
            user = get_user_model().objects.filter(is_superuser=True).first()
        except get_user_model().DoesNotFound:
            raise CommandError("No admin user found")

        self.stdout.write("SETUP GROUPS")
        PermissionService.setup_groups(user)

        self.stdout.write("SETUP ACTIVITY LOG MESSAGE TEMPLATES")

        sync_created = kwargs.get("sync_created", False)
        if sync_created:
            answer = input(
                "With sync_created is set, require some time to"
                " finish insert `created` log, continue (Y/n)? "
            )
            if not strtobool(answer):
                sync_created = False

        ActivityService.setup_templates(sync_created)

        self.stdout.write("SETUP TAG SETTINGS")
        TagService.setup_tags()

        self.stdout.write("DONE")
