import uuid

from ariadne import ObjectType

from ..core.decorators import validate_model
from ..core.models import Paginator
from .schemas import CustomerInputSchema, CustomerRead, CustomerUpdate
from .service import create, get, get_list, update

query = ObjectType("Query")
mutation = ObjectType("Mutation")


@query.field("get_customer")
def get_customer_by_id(_, info, id: str = None) -> dict:
    return {
        "ok": True,
        "customer": {
            "id": uuid.uuid4(),
            "internal_id": "ajshdq8w123",
            "profile": {"first_name": "Ha", "last_name": "Tran", "middle_name": None},
            "attributes": None,
        },
    }


@query.field("list_customers")
@validate_model(Paginator)
def list_customers(_, info, data=None) -> dict:
    pager_input = data.dict()
    customers, total = get_list(
        page_num=pager_input["page_num"],
        per_page=pager_input["per_page"],
        pre_per_page=pager_input["pre_per_page"],
        order_by=pager_input["order_by"],
    )
    return {"items": customers, "total": total}


@mutation.field("create_customer")
@validate_model(CustomerInputSchema)
def create_customer(_, info, data=None) -> dict:
    customer = create(data)
    return {"customer": {"id": customer.id}}


@mutation.field("update_customer")
@validate_model(CustomerUpdate, get)
def update_customer(_, info, instance=None, data=None) -> dict:
    instance = update(instance, data)
    return {"customer": {"id": instance.id}}


resolvers = [query, mutation]
