from django.core import management


def do_healthcheck():
    management.call_command('check', verbosity=1)
    print("Finish do_healthcheck")
