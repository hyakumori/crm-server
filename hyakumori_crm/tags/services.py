import logging
from uuid import UUID, uuid4

from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.models import ContentType
from django.db import connection, IntegrityError
from django.utils.translation import gettext as _

from hyakumori_crm.crm.models import Customer, Forest, get_user_model
from hyakumori_crm.tags.exceptions import ContentTypeNotFound, TagFieldNotExists, ObjectNotFound, DuplicatedTagSetting
from hyakumori_crm.tags.models import TagSetting
from hyakumori_crm.tags.schemas import TagSettingInput, AssignTagInput, TagKeyMigrateInput, TagKeyMigrateAllInput


class TagService:
    logger = logging.getLogger(__name__)

    @classmethod
    def get_content_type(cls, app_name: str, object_type: str):
        content_type = ContentType.objects.filter(app_label=app_name, model=object_type).first()
        if content_type is None:
            raise ContentTypeNotFound(_("Could not resolve content type for %(app_name)s, model %(object_type)s"
                                        % {'app_name': app_name, 'object_type': object_type}))
        return content_type

    @classmethod
    def setup_tags(cls):
        from hyakumori_crm.crm.common.constants import CUSTOMER_TAG_KEYS, FOREST_TAG_KEYS
        author = get_user_model().objects.filter(is_superuser=True).order_by("date_joined").first()

        # clean first
        TagSetting.objects.all().delete()

        for _type in [(Customer, CUSTOMER_TAG_KEYS), (Forest, FOREST_TAG_KEYS)]:
            content_type = ContentType.objects.get_for_model(_type[0])
            for k, v in _type[1].items():
                TagSetting.objects.create(content_type=content_type, name=v, code=k, user=author)

    @classmethod
    def get_setting_for_type(cls, app_name, object_type):
        content_type = cls.get_content_type(app_name, object_type)

        return TagSetting.objects.filter(content_type=content_type).all()

    @classmethod
    def get_tags_for_type(cls, app_name, object_type):
        """
        Return list of using tags with values
        dict(tag_name=["value1", "value2", "value3"])
        :param app_name:
        :param object_type:
        :return:
        """
        content_type = cls.get_content_type(app_name, object_type)

        try:
            model = content_type.model_class()
            table_name = model._meta.db_table
            with connection.cursor() as cursor:
                query = f"""
                       select distinct j1.key as key, j1.value as value
                       from {table_name}
                       cross join lateral jsonb_each(tags) j1
                       order by key, value
                    """
                cursor.execute(query)
                # columns = [col[0] for col in cursor.description]
                formatted_results = dict()
                for row in cursor.fetchall():
                    if formatted_results.get(row[0]) is None:
                        formatted_results[row[0]] = []
                    formatted_results[row[0]].append(row[1])

            return formatted_results
        except Exception as e:
            cls.logger.warning(str(e), e)
            return []

    @classmethod
    def create_tag_setting_for_type(cls, app_name, object_type, author: AbstractUser,
                                    tag_setting_input: TagSettingInput):
        content_type = cls.get_content_type(app_name, object_type)
        try:
            tag_setting = TagSetting(content_type=content_type,
                                     name=tag_setting_input.name,
                                     code=tag_setting_input.code,
                                     user=author)
            tag_setting.attributes["colors"] = list(map(lambda item: dict(value=item.value, color=item.color.as_hex()),
                                                        tag_setting_input.color_maps))
            tag_setting.save()
            return tag_setting
        except IntegrityError:
            raise DuplicatedTagSetting(_("Setting for tag %(tag)s already existed") % {"tag": tag_setting_input.name})

    @classmethod
    def update_tag_settings(cls, tag_setting_id, tag_setting_input: TagSettingInput):
        tag_setting = TagSetting.objects.filter(pk=tag_setting_id).first()
        if tag_setting is None:
            raise ObjectNotFound(_("Could not find tag setting %(id)s") % {'id': tag_setting_id})
        previous_tag_name = tag_setting.name
        tag_setting.name = tag_setting_input.name
        tag_setting.code = tag_setting_input.code
        tag_setting.attributes["colors"] = list(map(lambda item: dict(value=item.value, color=item.color.original()),
                                                    tag_setting_input.color_maps))
        tag_setting.save()
        content_type = tag_setting.content_type
        model = content_type.model_class()
        migrate_results = cls._do_migrate_all_tag_key(
            model._meta.db_table,
            TagKeyMigrateAllInput(from_key=previous_tag_name, to_key=tag_setting_input.name),
            do_update=True)
        return dict(tag=tag_setting,
                    migrate=dict(success=migrate_results[0], count=migrate_results[1]))

    @classmethod
    def assign_tag_for_object(cls, app_name, object_type, user, tag_input: AssignTagInput):
        content_type = cls.get_content_type(app_name, object_type)

        model = content_type.model_class()
        if not hasattr(model, "tags"):
            raise TagFieldNotExists(_("tags field not existed"))

        instance = model.objects.filter(pk=UUID(tag_input.object_id)).first()
        if instance is None:
            raise ObjectNotFound(_("Could not retrieve object: %(object_type)s, with ID: %(object_id)s")
                                 % {'object_type': object_type, 'object_id': tag_input.object_id})
        # get list of tags
        available_tags_for_types = cls.get_setting_for_type(app_name, object_type).values_list("name", flat=True)
        _before = dict(**instance.tags)

        instance.tags = dict()

        for tag in tag_input.tags:
            if tag.tag_name is not None and len(tag.tag_name) > 0:
                instance.tags[tag.tag_name] = tag.value

            if tag.tag_name not in available_tags_for_types:
                try:
                    cls.create_tag_setting_for_type(app_name, object_type, user, TagSettingInput(
                        name=tag.tag_name,
                        code=f"tag_{uuid4().hex[0:8]}",
                        color_maps=[]
                    ))
                except DuplicatedTagSetting:
                    continue

        instance.save()
        has_changed = _before != instance.tags

        return instance, has_changed

    @classmethod
    def delete_tag_settings(cls, tag_id):
        """
        Delete tag setting.
        Currently will keep object tags values.
        :param tag_id:
        :return:
        """
        tag_setting = TagSetting.objects.filter(pk=tag_id).first()
        if tag_setting is None:
            raise ObjectNotFound(_("Could not find tag setting %(id)s") % {'id': tag_id})
        tag_setting.delete()
        return tag_setting

    @classmethod
    def migrate_tag_key_objects(cls, app_name, object_type, migrate_input: TagKeyMigrateInput, do_update=False):
        content_type = cls.get_content_type(app_name, object_type)

        try:
            model = content_type.model_class()
            table_name = model._meta.db_table
            object_ids = ",".join(migrate_input.object_ids)
            with connection.cursor() as cursor:
                count_query = f"""
                    select count(*) as count
                    from {table_name}
                    where tags ? %s and id in (%s)
                """
                cursor.execute(count_query, (migrate_input.from_key, object_ids))
                result = cursor.fetchone()
                if do_update:
                    query = f"""
                         update {table_name}
                         set tags = tags - %s
                             || jsonb_build_object(%s, tags->%s)
                         where tags ? %s AND id IN (%s)
                    """
                    cursor.execute(query, (
                        migrate_input.from_key,
                        migrate_input.to_key,
                        migrate_input.from_key,
                        migrate_input.from_key,
                        object_ids,
                    ))

                return True, result[0]
        except Exception as e:
            cls.logger.exception(e)
            return False, 0

    @classmethod
    def migrate_tag_key_all_objects(cls, app_name, object_type, migrate_input: TagKeyMigrateAllInput, do_update=False):
        content_type = cls.get_content_type(app_name, object_type)

        try:
            model = content_type.model_class()
            table_name = model._meta.db_table
            return cls._do_migrate_all_tag_key(table_name, migrate_input, do_update)
        except Exception as e:
            cls.logger.exception(e)
            return False, 0

    @classmethod
    def _do_migrate_all_tag_key(cls, table_name, migrate_input, do_update):
        with connection.cursor() as cursor:
            count_query = f"""
                    select count(*) as count
                    from {table_name}
                    where tags ? %s
                """
            cursor.execute(count_query, (migrate_input.from_key,))
            result = cursor.fetchone()
            if do_update:
                query = f"""
                         update {table_name}
                         set tags = tags - %s
                             || jsonb_build_object(%s, tags->%s)
                         where tags ? %s
                    """
                cursor.execute(query, (
                    migrate_input.from_key,
                    migrate_input.to_key,
                    migrate_input.from_key,
                    migrate_input.from_key,
                ))
            return True, result[0]
