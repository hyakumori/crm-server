import querybuilder.query
import pydantic
from pydantic import errors
from typing import Any
from enum import Enum


class CompleteSorter(querybuilder.query.Sorter):
    def __init__(self, field=None, table=None, desc=False, nulls_last: bool = None):
        super().__init__(field=field, table=table, desc=desc)
        if nulls_last is None:
            self.nulls_last = True if not self.desc else False
        else:
            self.nulls_last = nulls_last

    def get_name(self, use_alias=True):
        name = super().get_name(use_alias=use_alias)
        if (self.nulls_last and not self.desc) or (not self.nulls_last and self.desc):
            return name
        return "{0} {1}".format(
            name, "NULLS LAST" if self.nulls_last else "NULLS FIRST"
        )


class Query(querybuilder.query.Query):
    def order_by(self, field=None, table=None, desc=False, nulls_last=None):
        self.sorters.append(
            CompleteSorter(field=field, table=table, desc=desc, nulls_last=nulls_last)
        )
        return self


class QueryWindow(querybuilder.query.QueryWindow, Query):
    pass


# TODO: provide documents for these patches
querybuilder.query.Sorter = CompleteSorter
querybuilder.query.Query = Query
querybuilder.query.QueryWindow = QueryWindow


def enum_validator(v: Any, field: "ModelField", config: "BaseConfig") -> Enum:
    try:
        enum_v = field.type_(v)
    except ValueError:
        # field.type_ should be an enum, so will be iterable
        enum_values = list(field.type_)
        permitted = ", ".join(repr(v.value) for v in enum_values)  # type: ignore
        raise errors.EnumError(enum_values=enum_values, permitted=permitted)
    return enum_v.value if config.use_enum_values else enum_v


pydantic.validators.enum_validator = enum_validator
# https://github.com/samuelcolvin/pydantic/blob/2eb62a3b2f/pydantic/validators.py#L500
pydantic.validators._VALIDATORS[0][1][1] = enum_validator
pydantic.validators._VALIDATORS[1][1][0] = enum_validator
