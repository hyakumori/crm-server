from filelock import FileLock, Timeout
from django.core.management.commands.runserver import Command as RunServerCommand


class Command(RunServerCommand):
    def handle(self, *args, **options):
        wpdevserver_lock = FileLock("wpdevserver.lock")
        try:
            wpdevserver_lock.acquire(timeout=1)
            import atexit
            from subprocess import Popen

            p = Popen(["yarn", "serve"], cwd="hyakumori_crm/static/hyakumori_crm")

            def release():
                p.terminate()
                wpdevserver_lock.release()

            atexit.register(release)
        except Timeout:
            pass
        super().handle(*args, **options)
