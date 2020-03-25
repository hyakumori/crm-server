from ariadne import make_executable_schema, load_schema_from_path, QueryType
from ariadne.contrib.django.scalars import date_scalar, datetime_scalar
from ariadne.contrib.django.views import GraphQLView

type_defs = load_schema_from_path("mamori/schema.graphql")

query1 = QueryType()


@query1.field("forests")
def resolve_forests(*_):
    return [{"id": "1234567890", "area": 112.5, "lat": 11.518721, "long": 30.123245,}]


query2 = QueryType()


@query2.field("forest_owner")
def resolve_forest_owner(*_, id=None):
    return {"id": 10}


schema = make_executable_schema(
    type_defs, [date_scalar, datetime_scalar, query1, query2]
)

view = GraphQLView.as_view(schema=schema)
