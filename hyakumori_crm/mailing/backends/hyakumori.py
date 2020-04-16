from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.backends.console import EmailBackend as ConsoleEmailBackend
from django.core.mail.backends.smtp import EmailBackend as SmtpEmailBackend


class EmailBackend(BaseEmailBackend):

    def __init__(self, *args, **kwargs):
        self._smtpBackend = SmtpEmailBackend(*args, **kwargs)
        self._consoleBackend = ConsoleEmailBackend(*args, **kwargs)
        super().__init__(**kwargs)

    def send_messages(self, email_messages):
        self._smtpBackend.send_messages(email_messages)
        if settings.DEBUG:
            self._consoleBackend.send_messages(email_messages)
