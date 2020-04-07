from ...core.models import BaseResourceModel, JSONField
from ..schemas.contract import Contract, ContractType
from ..schemas.forest import Cadastral, ForestOwner, GeoData, Tag


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
    def tag():
        return Tag().dict()

    @staticmethod
    def geodata():
        return GeoData().dict()


class Forest(BaseResourceModel):
    cadastral = JSONField(default=DefaultForest.cadastral, db_index=True)
    owner = JSONField(default=DefaultForest.owner, db_index=True)
    contracts = JSONField(default=DefaultForest.contracts, db_index=True)
    tag = JSONField(default=DefaultForest.tag)
    land_attributes = JSONField(default=dict)
    forest_attributes = JSONField(default=dict)
    geodata = JSONField(default=DefaultForest.geodata)
