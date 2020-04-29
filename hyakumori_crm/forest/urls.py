from rest_framework.routers import SimpleRouter
from django.urls import path
from .restful import (
    ForestViewSets,
    update_owners_view,
    set_default_customer_view,
    set_default_customer_contact_view,
)

router = SimpleRouter(trailing_slash=False)
router.register("forests", ForestViewSets, basename="forest")

api_urls = [
    path(
        "forests/<uuid:pk>/customers/update",
        view=update_owners_view,
        name="forests-customers-update",
    ),
    path(
        "forests/<uuid:pk>/customers/set-default",
        view=set_default_customer_view,
        name="forests-customers-set-default",
    ),
    path(
        "forests/<uuid:pk>/customers/set-default-contact",
        view=set_default_customer_contact_view,
        name="forests-customers-set-default-contact",
    ),
] + router.urls
