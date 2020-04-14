from django.urls import include, path
from djoser.views import UserViewSet, TokenDestroyView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .views import TokenObtainPairView

router = DefaultRouter()
router.register("users", UserViewSet, basename="user")

urlpatterns = [
    path("token/create/", TokenObtainPairView.as_view(), name="jwt-create"),
    path("token/refresh/", TokenRefreshView.as_view(), name="jwt-refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="jwt-verify"),
    path("", include(router.urls))
]
