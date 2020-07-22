import operator
from functools import reduce

from django.db.models import Q
from django.db.models.expressions import RawSQL
from django_filters import FilterSet, CharFilter


class TagsFilterSet(FilterSet):
    tags = CharFilter(method="has_tags_filter")

    @classmethod
    def get_tags_repr_queryset(cls, queryset):
        return queryset.annotate(
            tags_repr=RawSQL(
                """
              (select string_agg(tags_repr, ',') tags_repr
              from (
                select concat_ws(': ', key, value) as tags_repr
                from jsonb_each_text(tags) as x
              ) as ss)::text
            """,
                [],
            )
        )

    def get_tag_filter_conditions(self, name, value):
        values = list(set(map(lambda v: v.strip(), value.split(","))))
        if len(values) == 1 and values[0] == "":
            conditions = Q(**{"tags_repr__isnull": True}) | Q(
                **{"tags_repr__exact": None}
            )
        else:
            search_field_filter = "tags_repr__icontains"
            conditions = reduce(
                operator.or_,
                (
                    Q(**{search_field_filter: value})
                    for value in values
                    if len(value) > 0
                ),
            )
        return conditions

    def has_tags_filter(self, queryset, name, value):
        queryset = self.get_tags_repr_queryset(queryset)
        conditions = self.get_tag_filter_conditions(name, value)
        queryset = queryset.filter(conditions)
        return queryset
