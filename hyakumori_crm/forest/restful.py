import csv
import pathlib
import time

from django.core.cache import cache
from django.db import transaction
from django.db.models import Q, F, Count
from django.db.models.expressions import RawSQL
from django.http import HttpResponse, JsonResponse
from django.utils.translation import gettext_lazy as _
from rest_framework import mixins
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from hyakumori_crm.core.utils import default_paginator
from hyakumori_crm.crm.models import Forest, Archive, PostalHistory
from hyakumori_crm.crm.restful.serializers import (
    CustomerSerializer,
    LimittedCustomerSerializer,
    ForestSerializer,
    ContactSerializer,
    ArchiveSerializer,
)
from hyakumori_crm.crm.schemas.tag import TagBulkUpdate
from ..activity.services import ActivityService, ForestActions
from ..api.decorators import (
    api_validate_model,
    get_or_404,
)
from ..core.utils import clear_maintain_task_id_cache
from ..permissions.enums import SystemGroups

from .schemas import (
    ForestInput,
    forest_input_wrapper,
    OwnerPksInput,
    CustomerDefaultInput,
    CustomerContactDefaultInput,
    ForestMemoInput,
    ForestContractStatusBulkUpdate,
)
from .service import (
    get_forest_by_pk,
    update_basic_info,
    update_owners,
    get_forest_customers,
    get_customer_contacts_of_forest,
    set_default_customer,
    set_default_customer_contact,
    update_forest_memo,
    forest_csv_data_mapping,
    get_forests_for_csv,
    update_forest_tags,
    csv_headers,
    csv_upload,
    get_forests_tag_by_ids,
    bulk_update_forest_contact_status,
)
from .permissions import DownloadCsvPersmission


class ForestViewSets(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    serializer_class = ForestSerializer
    permission_classes = [Forest.model_perm_cls()]
    queryset = Forest.objects.all()

    @action(["GET"], detail=False, url_path="minimal")
    def list_minimal(self, request):
        query = (
            self.get_queryset()
            .annotate(customers_count=Count(F("forestcustomer__customer_id")))
            .annotate(
                tags_repr=RawSQL(
                    "select string_agg(tags_repr, ',') tags_repr "
                    "from ("
                    "select concat_ws(':', key, value) as tags_repr "
                    "from jsonb_each_text(tags) as x "
                    "where value is not null"
                    ") as ss",
                    params=[],
                )
            )
            .values(
                "id",
                "internal_id",
                "cadastral",
                "customers_count",
                "land_attributes",
                "attributes",
            )
        )
        search_str = request.GET.get("search")
        if search_str:
            query = query.filter(
                Q(pk__icontains=search_str)
                | Q(internal_id__icontains=search_str)
                | Q(cadastral__prefecture__icontains=search_str)
                | Q(cadastral__municipality__icontains=search_str)
                | Q(cadastral__sector__icontains=search_str)
                | Q(cadastral__subsector__icontains=search_str)
                | Q(tags_repr__icontains=search_str)
            )

        paginator = default_paginator()
        paged_list = paginator.paginate_queryset(
            request=request, queryset=query, view=self
        )
        return paginator.get_paginated_response(paged_list)

    @action(detail=True, methods=["GET"])
    def customers(self, request, **kwargs):
        obj = self.get_object()

        paginator = default_paginator()
        paged_list = paginator.paginate_queryset(
            request=request, queryset=get_forest_customers(obj.pk), view=self,
        )
        if request.user.member_of(SystemGroups.GROUP_LIMITED_USER):
            return paginator.get_paginated_response(
                LimittedCustomerSerializer(paged_list, many=True).data
            )
        else:
            return paginator.get_paginated_response(
                CustomerSerializer(paged_list, many=True).data
            )

    @action(["GET"], detail=True, url_path="archives")
    @get_or_404(
        get_func=get_forest_by_pk, to_name="forest", remove=True, pass_to="kwargs"
    )
    def archives(self, request, forest: Forest = None):
        archives = Archive.objects.filter(archiveforest__forest_id=forest.id)
        return Response(ArchiveSerializer(archives, many=True).data)

    @action(["GET"], detail=True, url_path="postal-histories")
    @get_or_404(
        get_func=get_forest_by_pk, to_name="forest", remove=True, pass_to="kwargs"
    )
    def postalhistories(self, request, forest: Forest = None):
        postalhistories = PostalHistory.objects.filter(
            postalhistoryforest__forest_id=forest.id
        )
        return Response(ArchiveSerializer(postalhistories, many=True).data)

    @action(detail=True, methods=["PUT", "PATCH"], url_path="basic-info")
    @get_or_404(get_func=get_forest_by_pk, to_name="forest", remove=True)
    @api_validate_model(forest_input_wrapper, "forest_in")
    def basic_info(self, request, *, forest_in: ForestInput):
        update_basic_info(forest_in.forest, forest_in)
        ActivityService.log(
            ForestActions.basic_info_updated, forest_in.forest, request=request
        )
        return Response({"id": forest_in.forest.pk})

    @action(detail=True, methods=["GET"], url_path="customers-forest-contacts")
    @get_or_404(get_forest_by_pk, to_name="forest", pass_to="kwargs", remove=True)
    def customers_forest_contacts(self, request, *, forest: Forest):
        contacts = get_customer_contacts_of_forest(forest.pk)
        paginator = default_paginator()
        paged_list = paginator.paginate_queryset(
            request=request, queryset=contacts, view=self
        )
        return paginator.get_paginated_response(
            ContactSerializer(paged_list, many=True).data
        )

    @action(detail=True, methods=["POST"], url_path="memo")
    @get_or_404(
        get_func=get_forest_by_pk, to_name="forest", remove=True,
    )
    @api_validate_model(ForestMemoInput)
    def update_memo(self, request, *, data: ForestMemoInput = None):
        forest, updated = update_forest_memo(data.forest, data.memo)
        if updated:
            ActivityService.log(
                ForestActions.memo_info_updated, data.forest, request=request
            )
        return Response({"memo": forest.attributes["memo"]})

    @action(
        detail=False,
        methods=["GET", "POST"],
        url_path="download-csv",
        permission_classes=[DownloadCsvPersmission],
    )
    def download_all_csv(self, request):
        if request.data is None or len(request.data) == 0:
            csv_data = get_forests_for_csv()
        else:
            csv_data = get_forests_for_csv(request.data)
        response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
        response["Content-Disposition"] = "attachment"
        headers = csv_headers()
        writer = csv.writer(response, dialect="excel")
        writer.writerow(headers)
        for forest in csv_data:
            csv_row = forest_csv_data_mapping(forest)
            writer.writerow(csv_row)
        return response

    @action(detail=False, methods=["PUT"], url_path="ids")
    def get_forests_by_ids(self, request):
        ids = request.data
        if ids is None or len(ids) == 0:
            return Response({"data": []})
        else:
            forest_tags = get_forests_tag_by_ids(ids)
            return JsonResponse(data={"data": forest_tags})

    @action(detail=False, methods=["PUT"], url_path="tags")
    @api_validate_model(TagBulkUpdate)
    def tags(self, request, data: TagBulkUpdate):
        update_forest_tags(data.dict())
        ActivityService.log_for_batch(
            ForestActions.tags_bulk_updated, Forest, obj_pks=data.ids, request=request
        )
        return Response({"msg": "OK"})

    @action(detail=False, methods=["POST"], url_path="upload-csv")
    def upload_csv(self, request):
        csv_file = request.data["file"]
        if pathlib.Path(csv_file.name).suffix != ".csv":
            return Response(
                {"errors": {"__root__": [_("Please upload a csv file!!")]}}, 400
            )
        pathlib.Path("media/upload/forest").mkdir(parents=True, exist_ok=True)
        file_name = f"{pathlib.Path(csv_file.name).stem}-{int(time.time())}.csv"
        fp = f"media/upload/forest/{file_name}"
        with open(fp, "wb+") as destination:
            for chunk in csv_file.chunks():
                destination.write(chunk)
        cache.set("maintain_task_id", f"forests/{file_name}", None)
        try:
            r = csv_upload(fp)
        except UnicodeDecodeError:
            transaction.set_rollback(True)
            return Response(
                {"errors": {"__root__": [_("Please upload a csv file!!")]}}, 400
            )
        else:
            if type(r) is int:
                return Response({"msg": "OK"}, status=200)
            else:
                transaction.set_rollback(True)
                return Response(r, status=400)
        finally:
            clear_maintain_task_id_cache()

    @action(detail=False, methods=["PUT"], url_path="contracts/status")
    @api_validate_model(ForestContractStatusBulkUpdate)
    def contract_status(self, request, data):
        ok = bulk_update_forest_contact_status(data)
        ActivityService.log_for_batch(
            ForestActions.bulk_contract_statuses_updated,
            Forest,
            obj_pks=data.pks,
            request=request,
        )
        return Response({"msg": ok})


@api_view(["PUT", "PATCH"])
@permission_classes([Forest.model_perm_cls()])
@get_or_404(get_func=get_forest_by_pk, to_name="forest", remove=True)
@api_validate_model(OwnerPksInput, "owner_pks_in")
def update_owners_view(request, *, owner_pks_in: OwnerPksInput):
    update_owners(owner_pks_in)
    ActivityService.log(
        ForestActions.customers_updated, owner_pks_in.forest, request=request
    )
    return Response({"id": owner_pks_in.forest.pk})


@api_view(["PUT", "PATCH"])
@permission_classes([Forest.model_perm_cls()])
@get_or_404(get_forest_by_pk, to_name="forest", remove=True)
@api_validate_model(CustomerDefaultInput)
def set_default_customer_view(request, *, data: CustomerDefaultInput = None):
    set_default_customer(data)
    ActivityService.log(ForestActions.customers_updated, data.forest, request=request)
    return Response({"id": data.forest.id})


@api_view(["PUT", "PATCH"])
@permission_classes([Forest.model_perm_cls()])
@get_or_404(get_forest_by_pk, to_name="forest", remove=True)
@api_validate_model(CustomerContactDefaultInput)
def set_default_customer_contact_view(
    request, *, data: CustomerContactDefaultInput = None
):
    set_default_customer_contact(data)
    ActivityService.log(ForestActions.customers_updated, data.forest, request=request)
    return Response({"id": data.forest.id})
