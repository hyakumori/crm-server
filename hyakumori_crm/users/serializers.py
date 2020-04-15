from django.utils.timezone import now
from djoser.serializers import (
    UserCreatePasswordRetypeSerializer as DjUserCreateSerializer,
)
from djoser.serializers import UserSerializer as DjUserSerializer
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenObtainSerializer,
)

from .models import User


class UserSerializer(DjUserSerializer):
    class Meta(DjUserSerializer.Meta):
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "profile",
            "settings",
        )
        read_only_fields = ("username", "email")


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
