from django.urls import path
from rest_framework.routers import SimpleRouter

from .restful import CustomerViewSets, contacts_list, customercontacts_list


router = SimpleRouter(trailing_slash=False)

router.register("customers", CustomerViewSets, basename="customer")

api_urls = router.urls + [
    path("contacts", view=contacts_list, name="contacts-list"),
    path("customercontacts", view=customercontacts_list, name="customercontacts-list"),
]
