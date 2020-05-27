import operator
from functools import reduce

from django.db.models import Q
from django_filters import FilterSet


class MultipleOrFilterSet(FilterSet):
    def icontains_filter(self, queryset, name, value):
        values = value.split(",")
        search_field_filter = name + "__icontains"
        queryset = queryset.filter(
            reduce(
                operator.or_, (Q(**{search_field_filter: value.strip()}) for value in values if len(value) > 0)
            )
        )
        return queryset
