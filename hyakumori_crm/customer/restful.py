from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_typed_views import typed_action

from hyakumori_crm.core.utils import default_paginator
from hyakumori_crm.crm.models import Customer
from hyakumori_crm.crm.restful.serializers import ContactSerializer, CustomerSerializer, ForestSerializer


class CustomerViewSets(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Customer.objects.all()

    @typed_action(detail=True, methods=["GET"], permission_classes=[IsAuthenticated])
    def contacts(self, request):
        obj = self.get_object()

        paginator = default_paginator()
        paged_list = paginator.paginate_queryset(request=request, queryset=obj.customercontact_set.all(), view=self)

        contacts = []
        for customer_contact in paged_list:
            # _contact = model_to_dict(customer_contact.contact, exclude="contact_info,deleted,author,editor")
            _contact = ContactSerializer(customer_contact.contact).data
            _contact["is_basic"] = customer_contact.is_basic
            contacts.append(_contact)

        return paginator.get_paginated_response(contacts)

    @typed_action(detail=True, methods=["GET"], permission_classes=[IsAuthenticated])
    def forests(self, request):
        obj = self.get_object()

        paginator = default_paginator()
        paged_list = paginator.paginate_queryset(request=request, queryset=obj.forestcustomer_set.all(), view=self)

        forests = []
        for forest_customer in paged_list:
            _forest = ForestSerializer(forest_customer.forest).data
            _contact = ContactSerializer(forest_customer.contact).data
            _forest["contact"] = _contact
            forests.append(_forest)

        return paginator.get_paginated_response(forests)

    @typed_action(detail=True, methods=["GET"])
    def representatives(self, request):
        return Response()

    @typed_action(detail=True, methods=["GET"])
    def related_archives(self, request):
        return Response()
