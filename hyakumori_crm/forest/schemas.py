from django_filters import FilterSet, CharFilter, DateFilter
from pydantic import validator

from ..core.models import Paginator
from ..crm.models import Forest


class ForestFilter(FilterSet):
    cadastral__prefecture = CharFilter(
        lookup_expr="icontains", method="icontains_filter"
    )
    cadastral__municipality = CharFilter(
        lookup_expr="icontains", method="icontains_filter"
    )
    cadastral__sector = CharFilter(lookup_expr="icontains", method="icontains_filter")
    cadastral__subsector = CharFilter(
        lookup_expr="icontains", method="icontains_filter"
    )
    owner__name_kana = CharFilter(lookup_expr="icontains", method="icontains_filter")
    owner__name_kanji = CharFilter(lookup_expr="icontains", method="icontains_filter")
    owner__address__prefecture = CharFilter(
        lookup_expr="icontains", method="icontains_filter"
    )
    owner__address__municipality = CharFilter(
        lookup_expr="icontains", method="icontains_filter"
    )
    owner__address__sector = CharFilter(
        lookup_expr="icontains", method="icontains_filter"
    )
    contracts__0__status = CharFilter(
        lookup_expr="icontains", method="icontains_filter"
    )
    contracts__0__start_date = DateFilter(method="exact_date_filter")
    contracts__0__end_date = DateFilter(method="exact_date_filter")
    contracts__1__status = CharFilter(
        lookup_expr="icontains", method="icontains_filter"
    )
    contracts__1__start_date = DateFilter(method="exact_date_filter")
    contracts__1__end_date = DateFilter(method="exact_date_filter")
    contracts__2__status = CharFilter(
        lookup_expr="icontains", method="icontains_filter"
    )
    contracts__2__start_date = DateFilter(method="exact_date_filter")
    contracts__2__end_date = DateFilter(method="exact_date_filter")
    tag__danchi = CharFilter(lookup_expr="icontains", method="icontains_filter")
    tag__manage_type = CharFilter(lookup_expr="icontains", method="icontains_filter")

    def icontains_filter(self, queryset, name, value):
        return queryset.filter(**{name + "__icontains": value})

    def exact_date_filter(self, queryset, name, value):
        return queryset.filter(**{name: value})

    class Meta:
        model = Forest
        fields = {"internal_id": ["icontains"]}


class ForestPaginator(Paginator):
    @validator("filters")
    def validate_filters(cls, filter_input):
        return ForestFilter(filter_input)
