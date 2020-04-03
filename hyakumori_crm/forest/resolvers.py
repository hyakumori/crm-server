from ariadne import ObjectType
from .service import get_all
import json
import os

query = ObjectType("Query")

@query.field("list_forests")
def get_list_forests(_, info) -> dict:
    return get_all()
    

resolvers = [query]
