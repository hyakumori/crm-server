import logging

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db import connection, transaction
from django_q.tasks import async_task

from hyakumori_crm.activity.constants import *  # noqa
from hyakumori_crm.activity.models import ActionLog
from hyakumori_crm.core.utils import get_remote_ip
from hyakumori_crm.crm.models import Customer, Forest
from hyakumori_crm.crm.models.message_template import MessageTemplate
from hyakumori_crm.slack.tasks import (
    notify as slack_notify,
    notify_for_batch as slack_notify_for_batch,
)


class ActivityService:
    logger = logging.getLogger(__name__)

    @classmethod
    def setup_templates(cls, sync_created=False):
        with transaction.atomic():
            MessageTemplate.objects.all().delete()

            ActivityService.import_message_templates(
                for_type="forest", action_class=ForestActions
            )
            ActivityService.import_message_templates(
                for_type="customer", action_class=CustomerActions
            )
            ActivityService.import_message_templates(
                for_type="archive", action_class=ArchiveActions
            )
            ActivityService.import_message_templates(
                for_type="postalhistory", action_class=PostalHistoryActions
            )
            ActivityService.import_message_templates(
                for_type="user", action_class=UserActions
            )

            if sync_created:
                ActionLog.objects.filter(
                    template_name__in=[
                        "forest.created",
                        "customer.created",
                        "archive.created",
                        "user.created",
                        "postalhistory.created",
                    ]
                ).all().delete()

                admin = (
                    get_user_model()
                    .objects.filter(is_superuser=True)
                    .order_by("date_joined")
                    .first()
                )
                for forest in Forest.objects.iterator():
                    ActivityService.log(
                        ForestActions.created,
                        forest,
                        user=admin,
                        created_at=forest.created_at,
                    )

                for customer in Customer.objects.iterator():
                    ActivityService.log(
                        CustomerActions.created,
                        customer,
                        user=admin,
                        created_at=customer.created_at,
                    )

                for user in get_user_model().objects.iterator():
                    ActivityService.log(
                        UserActions.created,
                        user,
                        user=admin,
                        created_at=user.date_joined,
                    )

    @classmethod
    def import_message_templates(cls, for_type: str, action_class):
        records = []
        actions = dict(
            [(k, v) for (k, v) in action_class.__dict__.items() if isinstance(v, tuple)]
        )
        for name, message in actions.items():
            content_type = ContentType.objects.get_for_model(ActionLog)
            name = message[0]
            template = message[1]
            icon = message[2]
            message_template = MessageTemplate(
                name=name,
                template=template,
                language="ja_JP",
                content_type=content_type,
            )
            message_template.attributes["icon"] = icon
            message_template.attributes["content_type"] = for_type
            records.append(message_template)

        return MessageTemplate.objects.bulk_create(records, ignore_conflicts=True)

    @classmethod
    def log(
        cls,
        action,
        model_instance,
        obj_pk=None,
        user=None,
        remote_ip=None,
        template_data=None,
        changes=None,
        request=None,
        created_at=None,
    ):
        """
        Usage:
        >>> from hyakumori_crm.crm.models import Forest
        >>> forest = Forest.objects.first()
        >>> ActivityService.log(ForestActions.created, forest)
        """

        if changes is None:
            changes = {}

        if request is not None:
            if remote_ip is None:
                remote_ip = get_remote_ip(request)
            if user is None and request.user is not None:
                user = request.user

        try:
            template_name = action[0] if isinstance(action, tuple) else action
            template = MessageTemplate.objects.get(name=template_name)
            content_type = ContentType.objects.get_for_model(model_instance)
            log = ActionLog.objects.create(
                content_type=content_type,
                object_pk=obj_pk if obj_pk is not None else model_instance.pk,
                template_name=template.name,
                template_data=template_data,
                changes=changes,
                user=user,
                remote_ip=remote_ip,
            )
            if created_at is not None:
                log.created_at = created_at
            async_task(
                slack_notify,
                message=template.template,
                user_fullname=user.full_name,
                dt=log.created_at,
                obj_title=model_instance.REPR_NAME,
                obj_name=model_instance.repr_name(),
                ack_failure=True,
            )
            return log.save(update_fields=["created_at"])
        except Exception as e:
            cls.logger.warning(
                f"Error while creating activity log for {action} {model_instance}",
                exc_info=e,
            )
            return ActionLog.objects.none()

    @classmethod
    def log_for_batch(
        cls,
        action,
        model_cls,
        obj_pks=None,
        user=None,
        remote_ip=None,
        template_data=None,
        changes=None,
        request=None,
        created_at=None,
    ):
        """
        Usage:
        >>> from hyakumori_crm.crm.models import Forest
        >>> forest = Forest.objects.first()
        >>> ActivityService.log(ForestActions.created, forest)
        """

        if changes is None:
            changes = {}

        if request is not None:
            if remote_ip is None:
                remote_ip = get_remote_ip(request)
            if user is None and request.user is not None:
                user = request.user

        try:
            template_name = action[0] if isinstance(action, tuple) else action
            template = MessageTemplate.objects.get(name=template_name)
            content_type = ContentType.objects.get_for_model(model_cls)
            logs = []
            for pk in obj_pks:
                log = ActionLog(
                    content_type=content_type,
                    object_pk=pk,
                    template_name=template.name,
                    template_data=template_data,
                    changes=changes,
                    user=user,
                    remote_ip=remote_ip,
                )
                if created_at is not None:
                    log.created_at = created_at
                logs.append(log)
            ActionLog.objects.bulk_create(logs)
            async_task(
                slack_notify_for_batch,
                message=template.template,
                user_fullname=user.full_name,
                dt=log.created_at,
                obj_title=model_cls.REPR_NAME,
                obj_names=list(
                    model_cls.objects.filter(pk__in=obj_pks).values_list(
                        model_cls.REPR_FIELD, flat=True
                    )
                ),
                ack_failure=True,
            )
        except Exception as e:
            cls.logger.warning(
                f"Error while creating activity log for {action} {model_cls}",
                exc_info=e,
            )
            return ActionLog.objects.none()

    @classmethod
    def get_log_for_object(cls, lang_code, app_label, object_type, object_id):
        content_type = ContentType.objects.filter(
            app_label=app_label, model=object_type
        ).first()
        action_content_type = ContentType.objects.get_for_model(ActionLog)
        try:
            with connection.cursor() as cursor:
                query = """
                    select
                        json_build_object(
                            'id',           al.user_id,
                            'first_name',   uu.first_name,
                            'last_name',    uu.last_name,
                            'email',        uu.email,
                            'username',     uu.username
                        ) as author,
                        al.id, -- extra select must be after json_build_object
                        al.changes, al.created_at, al.remote_ip, al.template_data,
                        cm.attributes->>'icon' as icon, cm.template
                    from activity_actionlog al
                    join crm_messagetemplate cm
                    on al.template_name = cm.name and cm.language=%s
                    join users_user uu on al.user_id = uu.id
                    where al.object_pk::uuid=%s::uuid and
                    al.content_type_id=%s
                    and cm.content_type_id=%s
                    order by al.created_at desc
                """
                cursor.execute(
                    query,
                    [lang_code, object_id, content_type.pk, action_content_type.pk],
                )
                columns = [col[0] for col in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return results
        except:
            return []
