import csv
import pathlib
import time

from django.core.cache import cache
from django.http.response import StreamingHttpResponse, JsonResponse
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.core.exceptions import ValidationError
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from hyakumori_crm.core.utils import (
    default_paginator,
    Echo,
    make_success_json,
    make_error_json,
)
from hyakumori_crm.crm.restful.serializers import (
    ContactSerializer,
    CustomerContactSerializer,
    CustomerSerializer,
    ArchiveSerializer,
)
from .schemas import (
    BankingInput,
    ContactsInput,
    CustomerContactsDeleteInput,
    CustomerInputSchema,
    CustomerUpdateSchema,
    ForestPksInput,
    ForestSerializer,
    CustomerMemoInput,
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
    get_customer_contacts_forests,
    customercontacts_list_with_search,
    get_list,
    get_customer_by_business_id,
    update_customer_tags,
    get_customers_tag_by_ids,
)
from .tasks import csv_upload
from ..activity.services import ActivityService, CustomerActions
from ..api.decorators import action_login_required, api_validate_model, get_or_404
from ..core.utils import clear_maintain_task_id_cache
from ..forest.service import parse_tags_for_csv


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
        return Response(
            {"id": customer.id, "business_id": customer.business_id}, status=201
        )

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

    @action(detail=True, methods=["GET"], url_path="contacts-forests")
    @get_or_404(
        get_func=get_customer_by_pk, to_name="customer", pass_to="kwargs", remove=True,
    )
    def contacts_forests(self, request, *, customer=None):
        forests = get_customer_contacts_forests(pk=customer.pk)
        return Response(ForestSerializer(forests, many=True).data)

    @action(detail=False, methods=["GET"], url_path="by-business-id")
    @action_login_required(with_permissions=["view_customer"])
    def get_customer_business_id(self, request):
        try:
            business_id = request.query_params.get("business_id", None)
            if business_id is None:
                return make_success_json(data={})
            customer = get_customer_by_business_id(business_id)
            return make_success_json(data=CustomerSerializer(customer).data)
        except ValueError as e:
            return make_error_json(message=str(e))

    @action(detail=False, methods=["PUT"], url_path="ids")
    # currently this api is using change status/tag actions,
    # the permission maybe change later
    @action_login_required(with_permissions=["change_customer"])
    def get_customers_by_ids(self, request):
        ids = request.data
        if ids is None or len(ids) == 0:
            return Response({"data": []})
        else:
            customer_tags = get_customers_tag_by_ids(ids)
            return JsonResponse(data={"data": customer_tags})

    @action(detail=False, methods=["PUT"], url_path="tags")
    @action_login_required(with_permissions=["change_customer"])
    def tags(self, request):
        update_customer_tags(request.data)
        return Response({"msg": "OK"})

    @action(detail=False, methods=["GET", "POST"])
    def download_csv(self, request):
        pks = request.data.get("ids", [])
        if len(pks) == 0:
            filters = None
        else:
            filters = Q(id__in=pks)
        try:
            customers = get_list(per_page=None, filters=filters)[0]
        except ValidationError:
            customers = []
        headers = [
            "\ufeff所有者ID",  # contains BOM char for opening on windows excel
            "土地所有者名（漢字）",
            "土地所有者名（カナ）",
            "土地所有者住所_都道府県",
            "土地所有者住所_市町村",
            "土地所有者住所_大字",
            "連絡先情報_郵便番号",
            "連絡先情報_電話番号",
            "連絡先情報_携帯電話",
            "連絡先情報_メールアドレス",
            "口座情報_銀行名",
            "口座情報_支店名",
            "口座情報_種別",
            "口座情報_口座番号",
            "口座情報_口座名義",
            _("Tag"),
        ]

        def generator(headers, rows):
            yield headers
            for row in rows:
                yield [
                    row["business_id"],
                    row["fullname_kanji"],
                    row["fullname_kana"],
                    row["prefecture"],
                    row["municipality"],
                    row["sector"],
                    row["postal_code"],
                    row["telephone"],
                    row["mobilephone"],
                    row["email"],
                    row["bank_name"],
                    row["bank_branch_name"],
                    row["bank_account_type"],
                    row["bank_account_number"],
                    row["bank_account_name"],
                    parse_tags_for_csv(row["tags"]),
                ]

        pseudo_buffer = Echo()
        writer = csv.writer(pseudo_buffer)
        response = StreamingHttpResponse(
            (writer.writerow(row) for row in generator(headers, customers)),
            content_type="text/csv",
        )
        response[
            "Content-Disposition"
        ] = 'application/octet-stream; filename="customers.csv"'
        return response

    @action(detail=False, methods=["POST"])
    def upload_csv(self, request):
        csv_file = request.data["file"]
        if pathlib.Path(csv_file.name).suffix != ".csv":
            return Response(
                {"errors": {"__root__": [_("Please upload a csv file!!")]}}, 400
            )
        pathlib.Path("media/upload/customer").mkdir(parents=True, exist_ok=True)
        file_name = f"{pathlib.Path(csv_file.name).stem}-{int(time.time())}.csv"
        fp = f"media/upload/customer/{file_name}"
        with open(fp, "wb+") as destination:
            for chunk in csv_file.chunks():
                destination.write(chunk)
        cache.set("maintain_task_id", f"customers/{file_name}", None)
        try:
            r = csv_upload(fp)
        except UnicodeDecodeError:
            return Response(
                {"errors": {"__root__": [_("Please upload a csv file!!")]}}, 400
            )
        else:
            if type(r) is int:
                return Response({"msg": "OK"}, status=200)
            else:
                return Response(r, status=400)
        finally:
            clear_maintain_task_id_cache()


@api_view(["GET"])
@action_login_required(with_permissions=["view_customer"])
def contacts_list(request):
    paginator = default_paginator()
    paged_list = paginator.paginate_queryset(
        request=request, queryset=contacts_list_with_search(request.GET.get("search")),
    )
    return paginator.get_paginated_response(
        ContactSerializer(paged_list, many=True).data
    )


@api_view(["GET"])
@action_login_required(with_permissions=["view_customer"])
def customercontacts_list(request):
    paginator = default_paginator()
    paged_list = paginator.paginate_queryset(
        request=request,
        queryset=customercontacts_list_with_search(request.GET.get("search")),
    )
    return paginator.get_paginated_response(
        CustomerContactSerializer(paged_list, many=True).data
    )
