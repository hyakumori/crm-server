from uuid import UUID

from django.db.models import Q, F, Count
from django.core.exceptions import ValidationError
from django.http import Http404
from rest_framework import viewsets, mixins
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_typed_views import Body, typed_action

from hyakumori_crm.core.utils import default_paginator
from hyakumori_crm.crm.models import Forest, Customer
from hyakumori_crm.crm.restful.serializers import CustomerSerializer, ForestSerializer

from ..api.decorators import (
    api_validate_model,
    get_or_404,
    typed_api_view,
    action_login_required,
)
from .schemas import (
    ForestInput,
    OwnerPksInput,
)
from .service import (
    get_customer_of_forest,
    get_forest_by_pk,
    update,
    update_owners,
)


class ForestViewSets(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    serializer_class = ForestSerializer

    def get_queryset(self):
        return Forest.objects.all()

    @action(["GET"], detail=False, url_path="minimal")
    def list_minimal(self, request):
        query = (
            self.get_queryset()
            .annotate(customers_count=Count(F("forestcustomer__customer_id")))
            .values("id", "internal_id", "cadastral", "customers_count")
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
            )

        paginator = default_paginator()
        paged_list = paginator.paginate_queryset(
            request=request, queryset=query, view=self
        )
        return paginator.get_paginated_response(paged_list)

    @action(detail=True, methods=["GET"], permission_classes=[IsAuthenticated])
    @action_login_required(
        with_policies=["can_view_forest_customer"]
    )  # TODO: implement policies check
    def customers(self, request, **kwargs):
        obj = self.get_object()

        paginator = default_paginator()
        paged_list = paginator.paginate_queryset(
            request=request,
            queryset=Customer.objects.filter(forestcustomer__forest_id=obj.pk)
            .forests_count()
            .prefetch_related("customercontact_set__contact")
            .order_by("id"),
            view=self,
        )

        return paginator.get_paginated_response(
            CustomerSerializer(paged_list, many=True).data
        )

    @typed_action(detail=True, methods=["GET"])
    def related_archives(self, request):
        return Response()

    @action(detail=True, methods=["PUT", "PATCH"], url_path="basic-info")
    @get_or_404(get_func=get_forest_by_pk, to_name="forest", remove=True)
    @api_validate_model(ForestInput, "forest_in")
    def basic_info(self, request, *, forest_in: ForestInput):
        update(forest_in.forest, forest_in.dict())
        return Response({"id": forest_in.forest.pk})


@api_view(["PUT", "PATCH"])
@get_or_404(get_func=get_forest_by_pk, to_name="forest", remove=True)
@api_validate_model(OwnerPksInput, "owner_pks_in")
def update_owners_view(request, *, owner_pks_in: OwnerPksInput):
    update_owners(owner_pks_in)
    return Response({"id": owner_pks_in.forest.pk})
