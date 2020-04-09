from ariadne import QueryType

from ..core.decorators import validate_model
from ..core.models import Paginator
from .service import get_forests_by_condition

query = QueryType()


@query.field("list_forests")
@validate_model(Paginator)
def get_list_forests(_, info, data) -> dict:
    pager_input = data.dict()
    forests, total = get_forests_by_condition(
        page_num=pager_input["page_num"],
        per_page=pager_input["per_page"],
        pre_per_page=pager_input["pre_per_page"],
        order_by=pager_input["order_by"],
    )
    return dict(forests=forests, total=total)


resolvers = [query]
