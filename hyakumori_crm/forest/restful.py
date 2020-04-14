from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_typed_views import typed_action

from hyakumori_crm.core.utils import default_paginator
from hyakumori_crm.crm.models import Forest
from hyakumori_crm.crm.restful.serializers import ContactSerializer, ForestSerializer


class ForestViewSets(viewsets.ModelViewSet):
    serializer_class = ForestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Forest.objects.all()

    @typed_action(detail=True, methods=["GET"], permission_classes=[IsAuthenticated])
    def customers(self, request):
        obj = self.get_object()

        paginator = default_paginator()
        paged_list = paginator.paginate_queryset(request=request, queryset=obj.forestcustomer_set.all(), view=self)

        customers = []
        for forest_customer in paged_list:
            _contact = ContactSerializer(forest_customer.contact).data
            _contact["customer_id"] = forest_customer.customer.pk
            customers.append(_contact)

        return paginator.get_paginated_response(customers)

    @typed_action(detail=True, methods=["GET"])
    def related_archives(self, request):
        return Response()
