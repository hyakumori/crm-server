from typing import Any
from graphql import GraphQLResolveInfo
from ariadne import QueryType
from django.utils.translation import gettext as _

from ..core.decorators import validate_model
from .service import get_forests_by_condition
from .schemas import ForestPaginator
from .filters import ForestFilter
from ..graphql.decorators import login_required

query = QueryType()


@query.field("foresttable_headers")
@login_required(with_policies=["can_view_forests"])
def get_foresttable_headers(obj: Any, info: GraphQLResolveInfo, **kwargs) -> dict:
    headers = [
        {"text": _("Forest ID"), "align": "right", "value": "internal_id"},
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
            "text": _("Lot Number"),
            "align": "center",
            "value": "land_attributes__地番本番",
            "sortable": False,
        },
        {
            "text": _("Owner name Kanji"),
            "align": "left",
            "value": "owner__name_kanji",
            "sortable": False,
        },
        {
            "text": _("Owner name Kana"),
            "align": "left",
            "value": "owner__name_kana",
            "sortable": False,
        },
        {
            "text": _("Contract type"),
            "align": "center",
            "value": "contract_type",
            "sortable": False,
        },
        {
            "text": _("Contract status"),
            "align": "center",
            "value": "contract_status",
            "sortable": False,
        },
        {
            "text": _("Contract start date"),
            "align": "center",
            "value": "contract_start_date",
            "sortable": False,
        },
        {
            "text": _("Contract end date"),
            "align": "center",
            "value": "contract_end_date",
            "sortable": False,
        },
        {
            "text": _("FSC certification participation"),
            "align": "center",
            "value": "fsc_status",
            "sortable": False,
        },
        {
            "text": _("FSC start"),
            "align": "center",
            "value": "fsc_start_date",
            "sortable": False,
        },
        {
            "text": _("FSC end"),
            "align": "center",
            "value": "fsc_end_date",
            "sortable": False,
        },
        {"text": _("Tag"), "align": "left", "value": "tags", "sortable": False},
    ]
    filters = {**ForestFilter.declared_filters, **ForestFilter.get_fields()}
    for header_define in headers:
        if header_define["value"] in filters:
            _filter = filters[header_define["value"]]
            header_define["filter_name"] = header_define["value"]

    return {"ok": True, "headers": headers}


@query.field("list_forests")
@login_required(with_policies=["can_view_forests"])
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
