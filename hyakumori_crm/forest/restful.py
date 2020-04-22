from uuid import UUID

from django.core.exceptions import ValidationError
from django.http import Http404
from rest_framework import viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_typed_views import Body, typed_action

from hyakumori_crm.core.utils import default_paginator
from hyakumori_crm.crm.models import Forest, Customer
from hyakumori_crm.crm.restful.serializers import CustomerSerializer, ForestSerializer

from ..api.decorators import api_validate_model, get_or_404, typed_api_view
from .schemas import (
    ForestInput,
    ForestOwnerContactsInput,
    OwnerPksInput,
)
from .service import (
    get_customer_of_forest,
    get_forest_by_pk,
    set_forest_owner_contacts,
    update,
    update_owners,
)


class ForestViewSets(viewsets.ModelViewSet):
    serializer_class = ForestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Forest.objects.all()

    @typed_action(detail=True, methods=["GET"], permission_classes=[IsAuthenticated])
    def customers(self, request):
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
@permission_classes([IsAuthenticated])
@get_or_404(get_func=get_forest_by_pk, to_name="forest", remove=True)
@api_validate_model(OwnerPksInput, "owner_pks_in")
def update_owners_view(request, *, owner_pks_in: OwnerPksInput):
    update_owners(owner_pks_in)
    return Response({"id": owner_pks_in.forest.pk})


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
@get_or_404(get_func=get_forest_by_pk, to_name="forest")
@get_or_404(
    get_func=get_customer_of_forest, to_name="customer", remove=True,
)
@api_validate_model(ForestOwnerContactsInput)
def set_contacts_to_owner_view(request, *, data: ForestOwnerContactsInput = None):
    set_forest_owner_contacts(data.forest, data)
    return Response({"id": data.forest.id})
