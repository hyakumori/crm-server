from uuid import UUID

from rest_framework import viewsets, mixins
from rest_framework.decorators import api_view, action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_typed_views import typed_action

from hyakumori_crm.core.utils import default_paginator
from hyakumori_crm.crm.models import Contact, Customer, ForestCustomer
from hyakumori_crm.crm.restful.serializers import ContactSerializer, CustomerSerializer

from ..api.decorators import api_validate_model, get_or_404
from .schemas import (
    ForestSerializer,
    CustomerContactsDeleteInput,
    CustomerInputSchema,
    ForestPksInput,
    ContactsInput,
    CustomerUpdateSchema,
    BankingInput,
)
from .service import (
    get_customer_contacts,
    get_customer_forests,
    contacts_list_with_search,
    delete_customer_contacts,
    get_customer_by_pk,
    create,
    update_forests,
    update_contacts,
    update_basic_info,
    update_banking_info,
    get_customers,
)


class CustomerViewSets(ViewSet):
    def list(self, request):
        search = request.GET.get("search")
        paginator = default_paginator()
        paged_list = paginator.paginate_queryset(
            request=request, queryset=get_customers(search), view=self,
        )
        return paginator.get_paginated_response(
            CustomerSerializer(paged_list, many=True).data
        )

    @get_or_404(get_customer_by_pk, to_name="customer", pass_to="kwargs", remove=True)
    def retrieve(self, request, customer=None):
        return Response(CustomerSerializer(customer).data)

    @api_validate_model(CustomerInputSchema)
    def create(self, request, data: dict = None):
        customer = create(data)
        return Response({"id": customer.id}, status=201)

    @get_or_404(get_customer_by_pk, to_name="customer", remove=True)
    @api_validate_model(CustomerUpdateSchema)
    def update(self, request, customer=None, data: dict = None):
        customer = update_basic_info(data)
        return Response({"id": customer.id})

    @action(["PUT", "PATCH"], detail=True, url_path="bank")
    @get_or_404(get_customer_by_pk, to_name="customer", pass_to="kwargs", remove=True)
    @api_validate_model(BankingInput)
    def update_customer_bank(self, request, customer=None, data: dict = None):
        customer = update_banking_info(customer, data)
        return Response({"id": customer.id})

    @action(detail=True, methods=["GET", "PUT", "PATCH"])
    @get_or_404(
        get_func=get_customer_by_pk,
        to_name="customer",
        pass_to=["request", "kwargs"],
        remove=True,
    )
    @api_validate_model(ContactsInput)
    def contacts(self, request, *, customer=None, data=None):
        if request.method == "GET":
            obj = customer
            paginator = default_paginator()
            paged_list = paginator.paginate_queryset(
                request=request, queryset=get_customer_contacts(obj.pk), view=self,
            )

            contacts = ContactSerializer(paged_list, many=True).data
            return paginator.get_paginated_response(contacts)
        else:
            update_contacts(data)
            return Response({"id": data.customer.id})

    @action(detail=True, methods=["GET", "PUT", "PATCH"])
    @get_or_404(
        get_func=get_customer_by_pk,
        to_name="customer",
        remove=True,
        pass_to=["request", "kwargs"],
    )
    @api_validate_model(ForestPksInput)
    def forests(self, request, *, customer=None, data: ForestPksInput = None):
        if request.method == "GET":
            obj = customer
            paginator = default_paginator()
            paged_list = paginator.paginate_queryset(
                request=request, queryset=get_customer_forests(obj.pk), view=self,
            )

            forests = ForestSerializer(paged_list, many=True).data
            return paginator.get_paginated_response(forests)
        else:
            update_forests(data)
            return Response({"id": data.customer.pk})

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
    def delete_contacts(self, request, *, data: CustomerContactsDeleteInput = None):
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
