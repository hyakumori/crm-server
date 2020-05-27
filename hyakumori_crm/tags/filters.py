import operator
from functools import reduce

from django.db.models import Q
from django.db.models.expressions import RawSQL
from django_filters import FilterSet, CharFilter


class TagsFilterSet(FilterSet):
    tags = CharFilter(method="has_tags_filter")

    @classmethod
    def get_tags_repr_queryset(cls, queryset):
        return queryset.annotate(tags_repr=RawSQL(
            """
              (select string_agg(tags_repr, ',') tags_repr
              from (
                select concat_ws(':', key, value) as tags_repr
                from jsonb_each_text(tags) as x
                where value is not null
              ) as ss)::text
            """, []))

    def has_tags_filter(self, queryset, name, value):
        queryset = self.get_tags_repr_queryset(queryset)
        values = value.split(",")
        queryset = queryset.filter(
            reduce(
                operator.or_, (Q(tags_repr__icontains=value.strip()) for value in values if len(value) > 0)
            )
        )
        return queryset


