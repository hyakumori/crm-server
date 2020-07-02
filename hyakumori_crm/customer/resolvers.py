from typing import Any

from ariadne import ObjectType
from django.utils.translation import gettext as _
from graphql import GraphQLResolveInfo

from hyakumori_crm.graphql.decorators import login_required
from .filters import CustomerFilter
from .schemas import CustomerPaginator
from .service import get_list
from ..core.decorators import validate_model

query = ObjectType("Query")


@query.field("customertable_headers")
@login_required(with_policies=["can_view_customers"])
def get_customertable_headers(obj: Any, info: GraphQLResolveInfo, **kwargs) -> dict:
    headers = [
        {"text": _(""), "value": "business_id", "align": "center"},
        {"text": _("Fullname Kanji"), "value": "fullname_kanji", "align": "left"},
        {"text": _("Fullname Kana"), "value": "fullname_kana", "align": "left"},
        {"text": _("Postal Code"), "value": "postal_code", "align": "center"},
        {"text": _("Prefecture"), "value": "prefecture", "align": "left"},
        {"text": _("Municipality"), "value": "municipality", "align": "left"},
        {"text": _("Address"), "value": "sector", "align": "left"},
        {"text": _("Telephone"), "value": "telephone", "align": "center"},
        {"text": _("Mobilephone"), "value": "mobilephone", "align": "center"},
        {"text": _("Email"), "value": "email", "align": "center"},
        {"text": _("Tag"), "value": "tags", "align": "left"},
    ]
    filters = CustomerFilter.get_filters()
    for header_define in headers:
        if header_define["value"] in filters:
            _filter = filters[header_define["value"]]
            header_define["filter_name"] = header_define["value"]

    return {"ok": True, "headers": headers}


@query.field("list_customers")
@login_required(with_policies=["can_view_customers"])
@validate_model(CustomerPaginator)
def list_customers(obj: Any, info: GraphQLResolveInfo, data=None, **kwargs) -> dict:
    pager_input = data.dict()
    customers, total = get_list(
        page_num=pager_input["page_num"],
        per_page=pager_input["per_page"],
        pre_per_page=pager_input["pre_per_page"],
        order_by=pager_input["order_by"],
        filters=pager_input["filters"],
    )
    return {"items": customers, "total": total}


resolvers = [query]
