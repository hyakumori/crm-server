from django.urls import include, path
from djoser.views import UserViewSet, TokenDestroyView
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .views import TokenObtainPairView

router = SimpleRouter(trailing_slash=False)
router.register("users", UserViewSet, basename="user")

api_urls = router.urls
api_urls += [
    path("token/create/", TokenObtainPairView.as_view(), name="jwt-create"),
    path("token/refresh/", TokenRefreshView.as_view(), name="jwt-refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="jwt-verify"),
]
