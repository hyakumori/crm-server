from ...core.models import BaseResourceModel, JSONField
from ..schemas.contract import Contract
from ..schemas.forest import Cadastral, ForestOwner, GeoData, Tag


class DefaultForest:
    @staticmethod
    def cadastral():
        return Cadastral().dict()

    @staticmethod
    def owner():
        return ForestOwner().dict()

    @staticmethod
    def contract():
        return Contract().dict()

    @staticmethod
    def tag():
        return Tag().dict()

    @staticmethod
    def geodata():
        return GeoData().dict()


class Forest(BaseResourceModel):
    cadastral = JSONField(default=DefaultForest.cadastral)
    owner = JSONField(default=DefaultForest.owner)
    contract = JSONField(default=DefaultForest.contract)
    tag = JSONField(default=DefaultForest.tag)
    geodata = JSONField(default=DefaultForest.geodata)
