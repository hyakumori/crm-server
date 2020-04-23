from django.contrib.auth.password_validation import validate_password
from django.db.models import Q
from django.utils.timezone import now
from djoser.conf import settings
from djoser.serializers import (
    UserCreateSerializer as DjUserCreateSerializer,
    ActivationSerializer as DjActivationSerializer,
    PasswordRetypeSerializer)
from djoser.serializers import UserSerializer as DjUserSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.relations import SlugRelatedField
from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenObtainSerializer,
)
from django.core import exceptions as django_exceptions
from django.utils.translation import gettext as _
from hyakumori_crm.permissions.services import PermissionService
from .models import User
from hyakumori_crm.permissions.enums import SystemGroups


def _is_user_self(request, instance):
    return request.user == instance


def _only_admin(request):
    return not request.user.is_anonymous and (request.user.is_superuser or request.user.member_of(
        SystemGroups.GROUP_ADMIN
    ))


class ActivationSerializer(DjActivationSerializer, PasswordRetypeSerializer):
    re_new_password = serializers.CharField(style={"input_type": "password"})
    new_password = serializers.CharField(style={"input_type": "password"})
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)

    default_error_messages = {
        "password_mismatch": settings.CONSTANTS.messages.PASSWORD_MISMATCH_ERROR,
        "stale_token": settings.CONSTANTS.messages.STALE_TOKEN_ERROR
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
        attrs = super().validate(attrs)
        if not self.user.is_active:
            return attrs
        raise PermissionDenied(self.error_messages["stale_token"])

    def validate(self, attrs):
        self._validate_password(attrs)
        self._validate_activation(attrs)
        return super().validate(attrs)


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

    def update_email(self, request, instance, errors):
        user = User.objects.filter(
            Q(email=request.data.get("email")) & (~Q(pk=instance.pk))
        ).exists()
        if user:
            errors["email"] = [_("Email existed")]
            return

        instance.email = request.data.get("email")

    def update_username(self, request, instance, errors):
        user = User.objects.filter(
            Q(username=request.data.get("username")) & (~Q(pk=instance.pk))
        ).exists()
        if user:
            errors["username"] = [_("Username existed")]
            return

        instance.username = request.data.get("username")

    def update_groups(self, request, instance):
        group = request.data.get("group")

        if _is_user_self(request, instance):
            return

        if group is None or group.get("value") is None:
            return

        group_id = [request.data.get("group").get("value")]
        PermissionService.assign_user_to_group(instance.pk, group_id, clear=True)

    def update_status(self, request, instance):
        status = request.data.get("is_active")
        if not _is_user_self(request, instance) and status is not None:
            instance.is_active = request.data.get("is_active")

    def update(self, instance, validated_data):
        request = self.context.get("request")

        if _only_admin(request):
            errors = dict()
            self.update_email(request, instance, errors)
            self.update_username(request, instance, errors)

            if len(errors.keys()) > 0:
                raise ValidationError(detail=errors)

            self.update_groups(request, instance)

            # update status
            self.update_status(request, instance)

        return ModelSerializer.update(self, instance, validated_data)


class UserCreateSerializer(DjUserCreateSerializer):
    class Meta(DjUserCreateSerializer.Meta):
        fields = DjUserCreateSerializer.Meta.fields + ("first_name", "last_name")

    def create(self, validated_data):
        request = self.context.get("request")
        # only allow admin to create user
        if _only_admin(request):
            return super().create(validated_data)
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
