from django.db.models.expressions import RawSQL
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from hyakumori_crm.core.permissions import AdminGroupPermission
from ..crm.schemas.contract import ContractTypeStatus

from .models import ContractType
from .serializers import ContractTypeSerializer


class ContractTypeViewSets(ModelViewSet):
    queryset = ContractType.objects.all()
    serializer_class = ContractTypeSerializer
    permission_classes = [AdminGroupPermission]
    pagination_class = None

    @action(detail=False, url_path="statuses", permission_classes=[IsAuthenticated])
    def get_statuses(self, request):
        statuses = dict()
        for status in ContractTypeStatus:
            statuses[status.name] = status.value
        return Response(data=statuses)

    @action(detail=False, url_path="active", permission_classes=[IsAuthenticated])
    def list_active(self, request):
        c = ContractType.objects.filter(attributes__assignable=True)
        return Response(ContractTypeSerializer(c, many=True).data)

    @action(methods=["PUT", "PATCH"], detail=True, url_path="toggle-active")
    def toggle_active(self, request, pk):
        active = request.data.get("active", True)
        ContractType.objects.filter(pk=pk).update(
            attributes=RawSQL(
                "attributes || jsonb_build_object('assignable', %s)", params=[active]
            )
        )
        return Response({"msg": "OK"})
