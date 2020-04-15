from django.urls import path
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .views import CustomUserViewSet, TokenObtainPairView

router = SimpleRouter(trailing_slash=False)
router.register("users", CustomUserViewSet, basename="user")

api_urls = router.urls
api_urls += [
    path("token/create/", TokenObtainPairView.as_view(), name="jwt-create"),
    path("token/refresh/", TokenRefreshView.as_view(), name="jwt-refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="jwt-verify"),
]
