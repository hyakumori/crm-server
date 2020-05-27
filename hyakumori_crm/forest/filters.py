import operator
from functools import reduce

from django.db.models import Q
from django_filters import CharFilter, DateFilter

from hyakumori_crm.crm.models import Forest
from hyakumori_crm.tags.filters import TagsFilterSet
from hyakumori_crm.core.filters import MultipleOrFilterSet


class ForestFilter(TagsFilterSet, MultipleOrFilterSet):
    internal_id = CharFilter(method="icontains_filter")
    cadastral__prefecture = CharFilter(method="icontains_filter")
    cadastral__municipality = CharFilter(method="icontains_filter")
    cadastral__sector = CharFilter(method="icontains_filter")
    cadastral__subsector = CharFilter(method="icontains_filter")
    owner__name_kana = CharFilter(method="owner_icontains_filter")
    owner__name_kanji = CharFilter(method="owner_icontains_filter")
    contracts__0__status = CharFilter(method="icontains_filter")
    contracts__0__start_date = DateFilter(method="exact_date_filter")
    contracts__0__end_date = DateFilter(method="exact_date_filter")
    contracts__1__status = CharFilter(method="icontains_filter")
    contracts__1__start_date = DateFilter(method="exact_date_filter")
    contracts__1__end_date = DateFilter(method="exact_date_filter")
    contracts__2__status = CharFilter(method="icontains_filter")
    contracts__2__start_date = DateFilter(method="exact_date_filter")
    contracts__2__end_date = DateFilter(method="exact_date_filter")

    def owner_icontains_filter(self, queryset, name, value):
        search_field = ""
        if name.find("name_kana") >= 0:
            search_field = f"attributes__customer_cache__repr_name_kana"
        if name.find("name_kanji") >= 0:
            search_field = f"attributes__customer_cache__repr_name_kanji"

        search_field_filter = search_field + "__icontains"
        values = value.split(" ")
        queryset = queryset.filter(
            reduce(
                operator.and_, (Q(**{search_field_filter: value.strip()}) for value in values if len(value) > 0)
            )
        )
        return queryset

    def exact_date_filter(self, queryset, name, value):
        return queryset.filter(**{name: value})

    class Meta:
        model = Forest
        fields = []
