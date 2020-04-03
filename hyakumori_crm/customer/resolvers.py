from functools import wraps
from ariadne import ObjectType

from ..core.decorators import validate_model
from ..core.models import Paginator
from .models import CustomerCreate, CustomerRead, CustomerUpdate
from .service import create, update, get, get_list

query = ObjectType("Query")
mutation = ObjectType("Mutation")


@query.field("get_customer")
def get_customer_by_id(_, info, id: str = None) -> dict:
    return {
        "ok": True,
        "customer": {
            "id": "asdaqw1273ajshdkc",
            "internal_id": "ajshdq8w123",
            "profile": {"first_name": "Ha", "last_name": "Tran", "middle_name": None},
            "attributes": None,
        },
    }


@query.field("list_customers")
@validate_model(Paginator)
def list_customers(_, info, data: dict = None) -> dict:
    customers, total = get_list(
        page_num=data["page_num"],
        per_page=data["per_page"],
        pre_per_page=data["pre_per_page"],
        order_by=data["order_by"],
    )
    return {"items": customers, "total": total}


@mutation.field("create_customer")
@validate_model(CustomerCreate)
def create_customer(_, info, data: dict = None) -> dict:
    customer = create(data)
    return {"customer": CustomerRead.from_orm(customer).dict()}


@mutation.field("update_customer")
@validate_model(CustomerUpdate, get)
def update_customer(_, info, instance=None, data: dict = None) -> dict:
    instance = update(instance, data)
    return {"customer": {"id": instance.id}}


resolvers = [query, mutation]
