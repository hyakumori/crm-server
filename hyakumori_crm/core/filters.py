import operator
from functools import reduce

from django.db.models import Q
from django_filters import FilterSet


class MultipleOrFilterSet(FilterSet):
    def icontains_filter(self, queryset, name, value):
        values = list(set(map(lambda v: v.strip(), value.split(","))))
        if len(values) == 1 and values[0] == "":
            conditions = Q(**{f"{name}__isnull": True}) | Q(**{f"{name}__exact": None})
        else:
            search_field_filter = name + "__icontains"
            conditions = reduce(
                operator.or_,
                (
                    Q(**{search_field_filter: value})
                    for value in values
                    if len(value) > 0
                ),
            )
        queryset = queryset.filter(conditions)
        return queryset
