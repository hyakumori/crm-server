from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from hyakumori_crm.core.utils import default_paginator
from hyakumori_crm.crm.restful.serializers import (
    ContactSerializer,
    CustomerSerializer,
    ArchiveSerializer,
)
from ..activity.services import ActivityService, CustomerActions
from ..api.decorators import action_login_required, api_validate_model, get_or_404

from .schemas import (
    BankingInput,
    ContactsInput,
    CustomerContactsDeleteInput,
    CustomerInputSchema,
    CustomerUpdateSchema,
    ForestPksInput,
    ForestSerializer,
    CustomerMemoInput,
    RequiredContactInput,
    ContactType,
    required_contact_input_wrapper,
)
from .service import (
    contacts_list_with_search,
    create,
    delete_customer_contacts,
    get_customer_by_pk,
    get_customer_contacts,
    get_customer_forests,
    get_customers,
    update_banking_info,
    update_basic_info,
    update_contacts,
    update_forests,
    update_customer_memo,
    create_contact,
    get_customer_archives,
)


class CustomerViewSets(ViewSet):
    @action_login_required(with_permissions=["view_customer"])
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
    @action_login_required(with_permissions=["view_customer"])
    def retrieve(self, request, customer=None):
        return Response(CustomerSerializer(customer).data)

    @api_validate_model(CustomerInputSchema)
    @action_login_required(with_permissions=["add_customer"])
    def create(self, request, data: dict = None):
        customer = create(data)
        ActivityService.log(CustomerActions.created, customer, request=request)
        return Response({"id": customer.id}, status=201)

    @get_or_404(get_customer_by_pk, to_name="customer", remove=True)
    @api_validate_model(CustomerUpdateSchema)
    @action_login_required(with_permissions=["change_customer"])
    def update(self, request, customer=None, data: dict = None):
        customer = update_basic_info(data)
        ActivityService.log(
            CustomerActions.basic_info_updated, customer, request=request
        )
        return Response({"id": customer.id})

    @action(["PUT", "PATCH"], detail=True, url_path="bank")
    @get_or_404(get_customer_by_pk, to_name="customer", pass_to="kwargs", remove=True)
    @api_validate_model(BankingInput)
    @action_login_required(with_permissions=["change_customer"])
    def update_customer_bank(self, request, customer=None, data: dict = None):
        customer, has_changed = update_banking_info(customer, data)
        if has_changed:
            ActivityService.log(
                CustomerActions.banking_info_updated, customer, request=request
            )
        return Response({"id": customer.id})

    @action(detail=True, methods=["GET", "PUT", "PATCH", "POST"])
    @get_or_404(
        get_func=get_customer_by_pk,
        to_name="customer",
        pass_to=["request", "kwargs"],
        remove=True,
    )
    @api_validate_model(ContactsInput, methods=["PUT", "PATCH"])
    @api_validate_model(required_contact_input_wrapper, methods=["POST"])
    @action_login_required(with_permissions=["change_customer", "view_customer"])
    def contacts(self, request, *, customer=None, data=None):
        if request.method == "GET":
            obj = customer
            paginator = default_paginator()
            paged_list = paginator.paginate_queryset(
                request=request, queryset=get_customer_contacts(obj.pk), view=self,
            )
            contacts = ContactSerializer(paged_list, many=True).data
            return paginator.get_paginated_response(contacts)
        elif request.method == "POST":
            contact = create_contact(customer, data)
            if data.contact_type == ContactType.family:
                action_type = CustomerActions.family_contacts_updated
            elif data.contact_type == ContactType.others:
                action_type = CustomerActions.other_contacts_updated
            ActivityService.log(action_type, customer, request=request)
            return Response({"id": contact.id}, status=201)
        else:
            update_contacts(data)
            ActivityService.log(
                CustomerActions.direct_contacts_updated, customer, request=request
            )
            return Response({"id": data.customer.id})

    @action(detail=True, methods=["GET", "PUT", "PATCH"])
    @get_or_404(
        get_func=get_customer_by_pk,
        to_name="customer",
        remove=True,
        pass_to=["request", "kwargs"],
    )
    @api_validate_model(ForestPksInput)
    @action_login_required(with_permissions=["change_forest"])
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
            ActivityService.log(
                CustomerActions.forests_updated, customer, request=request
            )
            return Response({"id": data.customer.pk})

    @action(detail=True, methods=["DELETE"], url_path="contacts")
    @get_or_404(
        get_func=get_customer_by_pk, to_name="customer", remove=True,
    )
    @api_validate_model(CustomerContactsDeleteInput)
    @action_login_required(with_permissions=["change_customer"])
    def delete_contacts(self, request, *, data: CustomerContactsDeleteInput = None):
        delete_customer_contacts(data)
        ActivityService.log(
            CustomerActions.direct_contacts_updated, data.customer, request=request
        )
        return Response({"id": data.forest.id})

    @action(detail=True, methods=["POST"], url_path="memo")
    @get_or_404(
        get_func=get_customer_by_pk, to_name="customer", remove=True,
    )
    @api_validate_model(CustomerMemoInput)
    @action_login_required(with_permissions=["change_customer"])
    def update_memo(self, request, *, data: CustomerMemoInput = None):
        customer, updated = update_customer_memo(data.customer, data.memo)

        if updated:
            ActivityService.log(
                CustomerActions.memo_info_updated, data.customer, request=request
            )
        return Response({"memo": customer.attributes["memo"]})

    @action(detail=True, methods=["GET"])
    @get_or_404(
        get_func=get_customer_by_pk, to_name="customer", pass_to="kwargs", remove=True,
    )
    @action_login_required(with_permissions=["change_customer", "view_customer"])
    def archives(self, request, *, customer=None):
        archives = get_customer_archives(customer.pk)
        return Response(ArchiveSerializer(archives, many=True).data)


@api_view(["GET"])
@action_login_required(with_permissions=["view_customer"])
def contacts_list(request):
    paginator = default_paginator()
    paged_list = paginator.paginate_queryset(
        request=request, queryset=contacts_list_with_search(request.GET.get("search"))
    )
    return paginator.get_paginated_response(
        ContactSerializer(paged_list, many=True).data
    )
