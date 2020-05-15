import uuid
from typing import Any
from ariadne import ObjectType
from graphql import GraphQLResolveInfo
from django.utils.translation import gettext as _

from hyakumori_crm.graphql.decorators import login_required
from ..core.decorators import validate_model
from .schemas import (
    CustomerInputSchema,
    CustomerRead,
    CustomerUpdate,
    CustomerFilter,
    CustomerPaginator,
)
from .service import get_list

query = ObjectType("Query")
mutation = ObjectType("Mutation")


@query.field("get_customer")
@login_required(with_policies=["can_view_customers"])
def get_customer_by_id(
    obj: Any, info: GraphQLResolveInfo, id: str = None, **kwargs
) -> dict:
    return {
        "ok": True,
        "customer": {
            "id": uuid.uuid4(),
            "internal_id": "ajshdq8w123",
            "profile": {"first_name": "Ha", "last_name": "Tran", "middle_name": None},
            "attributes": None,
        },
    }


@query.field("customertable_headers")
@login_required(with_policies=["can_view_customers"])
def get_customertable_headers(obj: Any, info: GraphQLResolveInfo, **kwargs) -> dict:
    headers = [
        {"text": _("Internal Id"), "value": "internal_id"},
        {"text": _("Fullname Kanji"), "value": "fullname_kanji"},
        {"text": _("Fullname Kana"), "value": "fullname_kana"},
        {"text": _("Postal Code"), "value": "postal_code"},
        {"text": _("Prefecture"), "value": "prefecture"},
        {"text": _("Municipality"), "value": "municipality"},
        {"text": _("Address"), "value": "address"},
        {"text": _("Ranking"), "value": "ranking"},
        {"text": _("Status"), "value": "status"},
        {"text": _("Same name"), "value": "same_name"},
        {"text": _("Telephone"), "value": "telephone"},
        {"text": _("Mobilephone"), "value": "mobilephone"},
        {"text": _("Email"), "value": "email"},
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


resolvers = [query, mutation]
