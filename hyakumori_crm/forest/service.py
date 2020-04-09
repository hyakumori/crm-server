from typing import Iterator, Union

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import connections
from django.db.utils import OperationalError

from ..crm.models.forest import Forest


def get_forests_by_condition(
    page_num: int = 1,
    per_page: int = 10,
    pre_per_page: Union[int, None] = None,
    order_by: Union[Iterator, None] = None,
):
    print(page_num, per_page, pre_per_page, order_by)
    offset = (pre_per_page or per_page) * (page_num - 1)
    if not order_by:
        order_by = []
    query = Forest.objects.all()
    total = query.count()
    forests = query.order_by(*order_by)[offset : offset + per_page]
    total = Forest.objects.count()
    return forests, total


# def get(pk):
#     try:
#         return Forest.objects.get(pk=pk)
#     except (Forest.DoesNotExist, ValidationError):
#         return None


# def create(data):
#     forest = Forest(**data)
#     forest.save()
#     return forest
