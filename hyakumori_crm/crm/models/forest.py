from django.core.serializers.json import DjangoJSONEncoder

from ...activity.constants import ForestActions
from ...core.models import BaseResourceModel, JSONField
from ..schemas.contract import Contract, ContractType
from ..schemas.forest import Cadastral, ForestOwner, GeoData, Tags


class DefaultForest:
    @staticmethod
    def cadastral():
        return Cadastral().dict()

    @staticmethod
    def owner():
        return ForestOwner().dict()

    @staticmethod
    def contracts():
        return [
            Contract(type=ContractType.long_term).dict(),
            Contract(type=ContractType.work_road).dict(),
            Contract(type=ContractType.fsc).dict(),
        ]

    @staticmethod
    def tags():
        return dict()

    @staticmethod
    def geodata():
        return GeoData().dict()


class Forest(BaseResourceModel):
    cadastral = JSONField(default=DefaultForest.cadastral, db_index=True)
    owner = JSONField(default=DefaultForest.owner, db_index=True)
    contracts = JSONField(
        default=DefaultForest.contracts, db_index=True, encoder=DjangoJSONEncoder
    )
    tags = JSONField(default=DefaultForest.tags)
    land_attributes = JSONField(default=dict)
    forest_attributes = JSONField(default=dict)
    geodata = JSONField(default=DefaultForest.geodata)

    class Meta:
        permissions = [
            ("manage_forest", "All permissions for forest"),
        ]

    @property
    def customers_count(self):
        return self.forestcustomer_set.all().count()

    @property
    def actions(self):
        return ForestActions
