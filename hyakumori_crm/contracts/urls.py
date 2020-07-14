from django.urls import path
from rest_framework.routers import SimpleRouter

from .restful import ContractTypeViewSets

router = SimpleRouter(trailing_slash=False)

router.register("contract_type", ContractTypeViewSets, basename="contract_type")

api_urls = router.urls + []
