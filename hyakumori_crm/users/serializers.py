from djoser.serializers import (UserCreatePasswordRetypeSerializer as DjUserCreateSerializer,
                                UserSerializer as DjUserSerializer)
from rest_framework_simplejwt.serializers import (TokenObtainPairSerializer,
                                                  TokenObtainSerializer)

from .models import User


class UserSerializer(DjUserSerializer):
    class Meta(DjUserSerializer.Meta):
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'profile', 'settings')
        read_only_fields = ('username', 'email')


class UserCreateSerializer(DjUserCreateSerializer):
    class Meta(DjUserCreateSerializer.Meta):
        fields = DjUserCreateSerializer.Meta.fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].required = False


# noinspection PyAbstractClass
class CustomTokenObtainSerializer(TokenObtainSerializer):
    username_field = User.EMAIL_FIELD


# noinspection PyAbstractClass
class CustomTokenObtainPairSerializer(CustomTokenObtainSerializer, TokenObtainPairSerializer):
    pass
