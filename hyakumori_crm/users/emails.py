from django.contrib.auth.tokens import default_token_generator
from templated_mail.mail import BaseEmailMessage

from djoser import utils
from djoser.conf import settings

from hyakumori_crm.activity.services import ActivityService, UserActions


class ActivationEmail(BaseEmailMessage):
    template_name = "email/activation.html"

    def get_context_data(self):
        context = super().get_context_data()

        user = context.get("user")
        # raw_password = context.get("view").request.data.get("password")
        # context["initial_password"] = raw_password
        context["uid"] = utils.encode_uid(user.pk)
        context["token"] = default_token_generator.make_token(user)
        context["url"] = settings.ACTIVATION_URL.format(**context)
        return context

    def send(self, to, *args, **kwargs):
        try:
            super().send(to, *args, **kwargs)
            context = super().get_context_data()
            user = context.get("user")
            request = context.get("view").request
            ActivityService.log(UserActions.email_invitation_sent, model_instance=user, request=request)
        except Exception as e:
            raise e
