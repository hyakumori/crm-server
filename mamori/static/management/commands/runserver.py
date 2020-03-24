import socket
from contextlib import closing
from django.core.management.commands.runserver import Command as RunServerCommand


class Command(RunServerCommand):
    def handle(self, *args, **options):
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            if sock.connect_ex(("localhost", 8080)) != 0:
                import atexit
                from subprocess import Popen

                p = Popen(["yarn", "serve"], cwd="mamori/static/mamori")
                atexit.register(p.terminate)
        super().handle(*args, **options)
