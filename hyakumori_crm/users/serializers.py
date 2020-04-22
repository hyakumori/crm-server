from django.db.models import Q
from django.utils.timezone import now
from djoser.serializers import (
    UserCreatePasswordRetypeSerializer as DjUserCreateSerializer,
)
from djoser.serializers import UserSerializer as DjUserSerializer
from rest_framework.exceptions import ValidationError, APIException
from rest_framework.relations import SlugRelatedField
from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenObtainSerializer,
)
from django.utils.translation import gettext as _
from hyakumori_crm.permissions.services import PermissionService
from .models import User
from hyakumori_crm.permissions.enums import SystemGroups


class UserSerializer(DjUserSerializer):
    groups = SlugRelatedField(many=True, read_only=True, slug_field="name")

    class Meta(DjUserSerializer.Meta):
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "profile",
            "settings",
            "last_login",
            "is_active",
            "groups",
        )
        read_only_fields = ("username", "email", "is_active")

    def _is_user_self(self, request, instance):
        return request.user == instance

    def _only_admin(self, request, instance):
        return request.user.is_superuser or request.user.member_of(
            SystemGroups.GROUP_ADMIN
        )

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

        if self._is_user_self(request, instance):
            return

        if group is None or group.get("value") is None:
            return

        group_id = [request.data.get("group").get("value")]
        PermissionService.assign_user_to_group(instance.pk, group_id, clear=True)

    def update_status(self, request, instance):
        status = request.data.get("is_active")
        if not self._is_user_self(request, instance) and status is not None:
            instance.is_active = request.data.get("is_active")

    def update(self, instance, validated_data):
        request = self.context.get("request")

        if self._only_admin(request, instance):
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
        fields = DjUserCreateSerializer.Meta.fields

    def __init__(self, *args, **kwargs):
        # self.fields["username"].required = False
        super().__init__(*args, **kwargs)


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
