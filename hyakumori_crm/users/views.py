from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework_simplejwt.views import TokenViewBase

from .models import User
from .serializers import CustomTokenObtainPairSerializer, UserSerializer
from ..core.permissions import IsUserOrReadOnly


class TokenObtainPairView(TokenViewBase):
    """
    Takes a set of user credentials and returns an access and refresh JSON web
    token pair to prove the authentication of those credentials.
    """
    serializer_class = CustomTokenObtainPairSerializer


token_obtain_pair = TokenObtainPairView.as_view()
