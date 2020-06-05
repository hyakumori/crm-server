from django.contrib.auth.password_validation import validate_password
from django.db.models import Q
from django.utils.timezone import now
from djoser.conf import settings
from djoser.serializers import (
    UserCreateSerializer as DjUserCreateSerializer,
    ActivationSerializer as DjActivationSerializer,
    UserSerializer as DjUserSerializer,
    UidAndTokenSerializer,
    PasswordRetypeSerializer,
)
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied
from pydantic.error_wrappers import ValidationError as PydanticValidationError
from rest_framework.relations import SlugRelatedField
from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenObtainSerializer,
)
from django.core import exceptions as django_exceptions
from django.utils.translation import gettext as _
from hyakumori_crm.permissions.services import PermissionService
from ..activity.constants import UserActions
from ..activity.services import ActivityService
from ..permissions import is_admin_request

from .models import User
from .types import UserUpdateInput


def _is_user_self(request, instance):
    return request.user == instance


def _only_admin(request):
    return not request.user.is_anonymous and is_admin_request(request)


class ActivationSerializer(DjActivationSerializer, PasswordRetypeSerializer):
    re_new_password = serializers.CharField(style={"input_type": "password"})
    new_password = serializers.CharField(style={"input_type": "password"})
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)

    default_error_messages = {
        "password_mismatch": settings.CONSTANTS.messages.PASSWORD_MISMATCH_ERROR,
        "stale_token": settings.CONSTANTS.messages.STALE_TOKEN_ERROR,
    }

    def _validate_password(self, attrs):
        if attrs["new_password"] != attrs["re_new_password"]:
            self.fail("password_mismatch")
        try:
            user = self.context["request"].user or self.user
            validate_password(attrs["new_password"], user)
        except django_exceptions.ValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})

    def _validate_activation(self, attrs):
        attrs = UidAndTokenSerializer.validate(self, attrs)
        if not self.user.is_active:
            return attrs
        raise PermissionDenied(self.error_messages["stale_token"])

    def validate(self, attrs):
        self._validate_password(attrs)
        return self._validate_activation(attrs)


class UserMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "full_name",
        )
        read_only_fields = ("username", "first_name", "last_name", "full_name")


class UserSerializer(DjUserSerializer):
    groups = SlugRelatedField(many=True, read_only=True, slug_field="name")

    class Meta(DjUserSerializer.Meta):
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "profile",
            "settings",
            "last_login",
            "is_active",
            "groups",
        )
        read_only_fields = ("username", "email", "is_active", "full_name")

    def update_email(self, _data, instance, errors):
        email = _data.email
        user = User.objects.filter(Q(email=email) & (~Q(pk=instance.pk))).exists()
        if user:
            errors["email"] = [_("Email existed")]
            return

        instance.email = email
        if instance.email != email:
            instance.email = email
            return True

        return False

    def update_username(self, _data, instance, errors):
        username = _data.username
        user = User.objects.filter(Q(username=username) & (~Q(pk=instance.pk))).exists()
        if user:
            errors["username"] = [_("Username existed")]
            return

        if instance.username != username:
            instance.username = username
            return True

        return False

    def update_groups(self, request, instance):
        group = request.data.get("group")

        if _is_user_self(request, instance):
            return

        if group is None or group.get("value") is None:
            return

        group_id = [group.get("value")]
        results = PermissionService.assign_user_to_group(
            instance.pk, group_id, clear=True
        )
        if results.get("has_changed"):
            ActivityService.log(
                UserActions.group_updated, model_instance=instance, request=request
            )

    def update_status(self, request, instance):
        status = request.data.get("is_active")
        if (
            not _is_user_self(request, instance)
            and status is not None
            and instance.is_active != status
        ):
            instance.is_active = status
            ActivityService.log(
                UserActions.status_updated, model_instance=instance, request=request
            )

    def update(self, instance, validated_data):
        request = self.context.get("request")

        if _only_admin(request):
            errors = dict()
            try:
                _data = UserUpdateInput(**request.data)
                has_email_update = self.update_email(_data, instance, errors)
                has_username_update = self.update_username(_data, instance, errors)

                if len(errors.keys()) > 0:
                    raise ValidationError(detail=errors)

                if has_email_update or has_username_update:
                    ActivityService.log(
                        UserActions.basic_info_updated,
                        model_instance=instance,
                        request=request,
                    )

            except PydanticValidationError as e:
                for error in e.errors():
                    errors[error.get("loc")[0]] = [error.get("msg")]
                raise ValidationError(detail=errors)

            # ignore if user is admin and attempting to update his groups and status
            if request.user != instance:
                self.update_groups(request, instance)
                # update status
                self.update_status(request, instance)

        has_basic_info_changed = (
            validated_data.get("first_name") != instance.first_name
            or validated_data.get("last_name") != instance.last_name
        )

        saved = ModelSerializer.update(self, instance, validated_data)

        if has_basic_info_changed:
            ActivityService.log(
                UserActions.basic_info_updated, model_instance=instance, request=request
            )

        return saved


class UserCreateSerializer(DjUserCreateSerializer):
    class Meta(DjUserCreateSerializer.Meta):
        fields = DjUserCreateSerializer.Meta.fields + ("first_name", "last_name")

    def create(self, validated_data):
        request = self.context.get("request")
        # only allow admin to create user
        if _only_admin(request):
            user = super().create(validated_data)
            ActivityService.log(
                UserActions.created, model_instance=user, request=request
            )
            return user
        else:
            raise PermissionDenied()


class CustomerTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        if self.user is not None and self.user.is_active:
            self.user.last_login = now()
            self.user.save()

        return data


# noinspection PyAbstractClass
class CustomTokenObtainSerializer(TokenObtainSerializer):
    username_field = User.EMAIL_FIELD


# noinspection PyAbstractClass
class CustomTokenObtainPairSerializer(
    CustomerTokenObtainPairSerializer, CustomTokenObtainSerializer
):
    pass
