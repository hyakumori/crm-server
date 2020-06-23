import operator
from functools import reduce

from django.db.models import Q
from django_filters import CharFilter

from hyakumori_crm.crm.models import Forest
from hyakumori_crm.tags.filters import TagsFilterSet
from hyakumori_crm.core.filters import MultipleOrFilterSet


class ForestFilter(TagsFilterSet, MultipleOrFilterSet):
    internal_id = CharFilter(method="icontains_filter")
    cadastral__municipality = CharFilter(method="icontains_filter")
    cadastral__sector = CharFilter(method="icontains_filter")
    land_attributes__地番本番 = CharFilter(method="icontains_filter")
    owner__name_kana = CharFilter(method="owner_icontains_filter")
    owner__name_kanji = CharFilter(method="owner_icontains_filter")
    contract_type = CharFilter(method="contract_icontains_filter")
    contract_status = CharFilter(method="contract_icontains_filter")
    contract_start_date = CharFilter(method="contract_icontains_filter")
    contract_end_date = CharFilter(method="contract_icontains_filter")
    fsc_status = CharFilter(method="fsc_icontains_filter")
    fsc_start_date = CharFilter(method="fsc_icontains_filter")
    fsc_end_date = CharFilter(method="fsc_icontains_filter")

    def _filter_name_with_space(self, search_field_filter, value):
        keywords = list(
            filter(
                lambda item: item is not None,
                map(lambda item: item if item else None, value.split(" ")),
            )
        )
        if len(keywords) > 0:
            return reduce(
                operator.and_,
                (
                    Q(**{search_field_filter: keyword.strip()})
                    for keyword in keywords
                    if len(keyword) > 0
                ),
            )
        return None

    def owner_icontains_filter(self, queryset, name, value):
        search_field = ""
        if name.find("name_kana") >= 0:
            search_field = "attributes__customer_cache__repr_name_kana"
        if name.find("name_kanji") >= 0:
            search_field = "attributes__customer_cache__repr_name_kanji"

        search_field_filter = search_field + "__icontains"
        keywords = value.replace("\u3000", "").split(",")
        filters = []
        for keyword in keywords:
            _f = self._filter_name_with_space(search_field_filter, keyword)
            if _f is not None:
                filters.append(_f)
        query = Q()
        for _f in filters:
            query |= _f
        queryset = queryset.filter(query)

        return queryset

    def fsc_icontains_filter(self, queryset, name, value):
        suffix_name = name.split("fsc_")[-1]
        filter_name = "contracts__-1__" + suffix_name
        return super().icontains_filter(queryset, filter_name, value)

    def contract_icontains_filter(self, queryset, name, value):
        suffix_name = name.split("contract_")[-1]
        filter_name = "contracts__0__" + suffix_name
        return super().icontains_filter(queryset, filter_name, value)

    class Meta:
        model = Forest
        fields = []
