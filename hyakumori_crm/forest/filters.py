import operator
from functools import reduce

from django.db.models import Q, Subquery
from django.db.models.expressions import RawSQL
from django_filters import CharFilter

from hyakumori_crm.crm.models import Forest
from hyakumori_crm.tags.filters import TagsFilterSet
from hyakumori_crm.core.filters import MultipleOrFilterSet


class ForestFilter(TagsFilterSet, MultipleOrFilterSet):
    internal_id = CharFilter(method="icontains_filter")
    cadastral__municipality = CharFilter(method="icontains_filter")
    cadastral__sector = CharFilter(method="icontains_filter")
    land_attributes__地番本番 = CharFilter(method="icontains_filter")
    land_attributes__地番支番 = CharFilter(method="icontains_filter")
    owner__name_kana = CharFilter(method="owner_icontains_filter")
    owner__name_kanji = CharFilter(method="owner_icontains_filter")
    contract_type = CharFilter(method="contract_icontains_filter")
    contract_status = CharFilter(method="contract_icontains_filter")
    contract_start_date = CharFilter(method="contract_icontains_filter")
    contract_end_date = CharFilter(method="contract_icontains_filter")
    fsc_status = CharFilter(method="fsc_icontains_filter")
    fsc_start_date = CharFilter(method="fsc_icontains_filter")

    @property
    def qs(self):
        return super().qs.annotate(
            contracts_json=RawSQL(
                """json_build_object(
'contract_type', contracts->0->>'type',
'contract_status', contracts->0->>'status',
'contract_start_date', contracts->0->>'start_date',
'contract_end_date', contracts->0->>'end_date',
'fsc_status', contracts->-1->>'status',
'fsc_start_date', contracts->-1->>'start_date'
)""",
                params=[],
            ),
        )

    @classmethod
    def get_tags_repr_queryset(cls, queryset):
        queryset = super().get_tags_repr_queryset(queryset)
        return queryset.annotate(
            customer_tags_repr=RawSQL(
                """select full_tag from (
    select A2.forest_id,
        array_to_string(array_agg(distinct A2.full_tag), ',') as full_tag
    from (
        select A1.forest_id, unnest(A1.full_tag) as full_tag
        from (
            select fc.forest_id,
                (select array_agg(concat_ws(':', KEY, value)) AS full_tag
                    FROM jsonb_each_text(c.tags)
                    WHERE value IS NOT NULL)
            from crm_forestcustomer fc
            join crm_customer c on c.id = fc.customer_id
            where c.tags != '{}'::jsonb
            and forest_id = crm_forest.id
        ) A1
    ) A2
    group by A2.forest_id
) A3 where forest_id = crm_forest.id""",
                params=[],
            ),
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
                    *[
                        Q(**{search_field_filter: value})
                        for value in values
                        if len(value) > 0
                    ],
                    *(
                        Q(**{"customer_tags_repr__icontains": value})
                        for value in values
                        if len(value) > 0
                    ),
                ),
            )
        return conditions

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
