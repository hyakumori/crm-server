from rest_framework.routers import SimpleRouter
from django.urls import path
from .restful import ForestViewSets, update_owners_view, set_contacts_to_owner_view

router = SimpleRouter(trailing_slash=False)
router.register("forests", ForestViewSets, basename="forest")

api_urls = [
    path(
        "forests/<uuid:pk>/customers/update",
        view=update_owners_view,
        name="forests-customers-update",
    ),
    path(
        "forests/<uuid:pk>/customers/<uuid:customer_pk>/set-contact",
        view=set_contacts_to_owner_view,
        name="forests-customer-set-contact",
    ),
] + router.urls
