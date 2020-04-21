from rest_framework import viewsets
from rest_framework.decorators import api_view, action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_typed_views import typed_action

from hyakumori_crm.core.utils import default_paginator
from hyakumori_crm.crm.models import Contact, Customer, ForestCustomer
from hyakumori_crm.crm.restful.serializers import ContactSerializer, CustomerSerializer

from ..api.decorators import api_validate_model, get_or_404
from .schemas import ForestSerializer, CustomerContactsDeleteInput
from .service import (
    get_customer_contacts,
    get_customer_forests,
    contacts_list_with_search,
    delete_customer_contacts,
    get_customer_by_pk,
)


class CustomerViewSets(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Customer.objects.all()

    @typed_action(detail=True, methods=["GET"], permission_classes=[IsAuthenticated])
    def contacts(self, request):
        obj = self.get_object()

        paginator = default_paginator()
        paged_list = paginator.paginate_queryset(
            request=request, queryset=get_customer_contacts(obj.pk), view=self,
        )

        contacts = ContactSerializer(paged_list, many=True).data
        return paginator.get_paginated_response(contacts)

    @typed_action(detail=True, methods=["GET"], permission_classes=[IsAuthenticated])
    def forests(self, request):
        obj = self.get_object()

        paginator = default_paginator()
        paged_list = paginator.paginate_queryset(
            request=request, queryset=get_customer_forests(obj.pk), view=self,
        )

        forests = ForestSerializer(paged_list, many=True).data
        return paginator.get_paginated_response(forests)

    @typed_action(detail=True, methods=["GET"])
    def representatives(self, request):
        return Response()

    @typed_action(detail=True, methods=["GET"])
    def related_archives(self, request):
        return Response()

    @action(detail=True, methods=["DELETE"], url_path="contacts")
    @get_or_404(
        get_func=get_customer_by_pk, to_name="customer", remove=True,
    )
    @api_validate_model(CustomerContactsDeleteInput)
    def delete_contacts(request, *, data: CustomerContactsDeleteInput = None):
        delete_customer_contacts(data)
        return Response({"id": data.forest.id})


@api_view(["GET"])
def contacts_list(request):
    paginator = default_paginator()
    paged_list = paginator.paginate_queryset(
        request=request, queryset=contacts_list_with_search(request.GET.get("search"))
    )
    return paginator.get_paginated_response(
        ContactSerializer(paged_list, many=True).data
    )
