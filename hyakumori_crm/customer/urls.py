from rest_framework.routers import SimpleRouter
from .restful import CustomerViewSets

router = SimpleRouter(trailing_slash=False)

router.register("customers", CustomerViewSets, basename="customer")

api_urls = router.urls
