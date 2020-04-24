from rest_framework.routers import SimpleRouter
from django.urls import path
from .restful import ForestViewSets, update_owners_view

router = SimpleRouter(trailing_slash=False)
router.register("forests", ForestViewSets, basename="forest")

api_urls = [
    path(
        "forests/<uuid:pk>/customers/update",
        view=update_owners_view,
        name="forests-customers-update",
    ),
] + router.urls
