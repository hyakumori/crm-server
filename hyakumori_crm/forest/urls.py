from rest_framework.routers import SimpleRouter
from django.urls import path
from .restful import ForestViewSets, update

router = SimpleRouter(trailing_slash=False)
router.register("forests", ForestViewSets, basename="forest")

api_urls = router.urls
