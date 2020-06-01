from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import ContractType
from .serializers import ContractTypeSerializer
from ..crm.schemas.contract import ContractTypeStatus
from ..permissions import IsAdminOrReadOnly


class ContractTypeViewSets(ModelViewSet):
    queryset = ContractType.objects.all()
    serializer_class = ContractTypeSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = None

    @action(detail=False, url_path="statuses", permission_classes=[IsAdminOrReadOnly])
    def get_statuses(self, request):
        statuses = dict()
        for status in ContractTypeStatus:
            statuses[status.name] = status.value
        return Response(data=statuses)
