from ariadne import make_executable_schema, load_schema_from_path, QueryType
from ariadne.contrib.django.scalars import date_scalar, datetime_scalar
from ariadne.contrib.django.views import GraphQLView

from hyakumori_crm.customer.types import types as customers_types
from hyakumori_crm.forest.types import types as forests_types

from hyakumori_crm.customer.resolvers import resolvers as customers_resolvers
from hyakumori_crm.forest.resolvers import resolvers as forest_resolvers

from .types import types as common_types
from .scalars import json_scalar


type_defs = [common_types, customers_types, forests_types]

schema = make_executable_schema(
    type_defs,
    [
        date_scalar,
        datetime_scalar,
        json_scalar,
        *customers_resolvers,
        *forest_resolvers,
    ],
)


view = GraphQLView.as_view(schema=schema)
