from django.contrib.auth.models import AbstractUser

from ..schemas.forest import ForestSchema
from ..models.forest import Forest


class ForestService:
    @staticmethod
    def create_forest(customer: ForestSchema, author: AbstractUser) -> Forest:
        pass

