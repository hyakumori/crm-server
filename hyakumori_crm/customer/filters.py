from django_filters import CharFilter

from hyakumori_crm.crm.models import Customer
from hyakumori_crm.tags.filters import TagsFilterSet
from hyakumori_crm.core.filters import MultipleOrFilterSet


class CustomerFilter(MultipleOrFilterSet):
    internal_id = CharFilter(method="icontains_filter")
    business_id = CharFilter(method="icontains_filter")
    fullname_kanji = CharFilter(method="icontains_filter")
    fullname_kana = CharFilter(method="icontains_filter")
    postal_code = CharFilter(method="icontains_filter")
    address = CharFilter(method="icontains_filter")
    telephone = CharFilter(method="icontains_filter")
    mobilephone = CharFilter(method="icontains_filter")
    prefecture = CharFilter(method="icontains_filter")
    municipality = CharFilter(method="icontains_filter")
    email = CharFilter(method="icontains_filter")
    tags = CharFilter(method="icontains_filter")

    class Meta:
        model = Customer
        fields = []
