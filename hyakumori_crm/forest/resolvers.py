from typing import Any
from graphql import GraphQLResolveInfo
from ariadne import QueryType
from django.utils.translation import gettext as _

from ..core.decorators import validate_model
from .service import get_forests_by_condition
from .schemas import ForestFilter, ForestPaginator
from ..graphql.decorators import login_required

query = QueryType()


@query.field("foresttable_headers")
@login_required(with_policies=['can_view_forests'])
def get_foresttable_headers(obj: Any, info: GraphQLResolveInfo, **kwargs) -> dict:
    headers = [
        {"text": _("Forest ID"), "align": "right", "value": "internal_id"},
        {
            "text": _("Prefecture"),
            "align": "center",
            "value": "cadastral__prefecture",
            "sortable": False,
        },
        {
            "text": _("Municipality"),
            "align": "center",
            "value": "cadastral__municipality",
            "sortable": False,
        },
        {
            "text": _("Sector"),
            "align": "center",
            "value": "cadastral__sector",
            "sortable": False,
        },
        {
            "text": _("Subsector"),
            "align": "center",
            "value": "cadastral__subsector",
            "sortable": False,
        },
        {
            "text": _("Owner name Kanji"),
            "align": "center",
            "value": "owner__name_kanji",
            "sortable": False,
        },
        {
            "text": _("Owner name Kana"),
            "align": "center",
            "value": "owner__name_kana",
            "sortable": False,
        },
        {
            "text": _("Owner address prefecture"),
            "align": "center",
            "value": "owner__address__prefecture",
            "sortable": False,
        },
        {
            "text": _("Owner address municipality"),
            "align": "center",
            "value": "owner__address__municipality",
            "sortable": False,
        },
        {
            "text": _("Owner address sector"),
            "align": "center",
            "value": "owner__address__sector",
            "sortable": False,
        },
        {
            "text": _("Long term contract"),
            "align": "center",
            "value": "contracts__0__status",
            "sortable": False,
        },
        {
            "text": _("Long term start"),
            "align": "center",
            "value": "contracts__0__start_date",
            "sortable": False,
        },
        {
            "text": _("Long term end"),
            "align": "center",
            "value": "contracts__0__end_date",
            "sortable": False,
        },
        {
            "text": _("Work load contract"),
            "align": "center",
            "value": "contracts__1__status",
            "sortable": False,
        },
        {
            "text": _("Work load start"),
            "align": "center",
            "value": "contracts__1__start_date",
            "sortable": False,
        },
        {
            "text": _("Work load end"),
            "align": "center",
            "value": "contracts__1__end_date",
            "sortable": False,
        },
        {
            "text": _("FSC certification participation"),
            "align": "center",
            "value": "contracts__2__status",
            "sortable": False,
        },
        {
            "text": _("FSC start"),
            "align": "center",
            "value": "contracts__2__start_date",
            "sortable": False,
        },
        {
            "text": _("FSC end"),
            "align": "center",
            "value": "contracts__2__end_date",
            "sortable": False,
        },
        {
            "text": _("Tag danchi"),
            "align": "center",
            "value": "tag__danchi",
            "sortable": False,
        },
        {
            "text": _("Tag Manage Type"),
            "align": "center",
            "value": "tag__manage_type",
            "sortable": False,
        },
    ]
    filters = {**ForestFilter.declared_filters, **ForestFilter.get_fields()}
    for header_define in headers:
        if header_define["value"] in filters:
            _filter = filters[header_define["value"]]
            header_define["filter_name"] = header_define["value"]

    return {"ok": True, "headers": headers}


@query.field("list_forests")
@login_required(with_policies=['can_view_forests'])
@validate_model(ForestPaginator)
def get_list_forests(obj, info, data, **kwargs) -> dict:
    pager_input = data.dict()
    forests, total = get_forests_by_condition(
        page_num=pager_input["page_num"],
        per_page=pager_input["per_page"],
        pre_per_page=pager_input["pre_per_page"],
        order_by=pager_input["order_by"],
        filters=pager_input["filters"],
    )
    return dict(forests=forests, total=total)


resolvers = [query]
