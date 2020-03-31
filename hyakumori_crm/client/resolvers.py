from functools import wraps
from ariadne import ObjectType

from ..core.decorators import validate_model
from .models import ClientCreate, ClientRead, ClientUpdate
from .service import create, update, get

query = ObjectType("Query")
mutation = ObjectType("Mutation")


@query.field("get_client")
def get_client_by_id(_, info, id: str = None) -> dict:
    return {
        "ok": True,
        "client": {
            "id": "asdaqw1273ajshdkc",
            "internal_id": "ajshdq8w123",
            "profile": {"first_name": "Ha", "last_name": "Tran", "middle_name": None},
            "attributes": None,
        },
    }


@mutation.field("create_client")
@validate_model(ClientCreate)
def create_client(_, info, data: dict = None) -> dict:
    client = create(data)
    return {"client": ClientRead.from_orm(client).dict()}


@mutation.field("update_client")
@validate_model(ClientUpdate, get)
def update_client(_, info, instance=None, data: dict = None) -> dict:
    instance = update(instance, data)
    return {"client": {"id": instance.id}}


resolvers = [query, mutation]
