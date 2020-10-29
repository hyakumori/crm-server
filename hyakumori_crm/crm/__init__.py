from typing import Any, Dict, Type, Union, Sequence
from enum import Enum

import querybuilder.query
import pydantic
from pydantic import errors
from pydantic.error_wrappers import get_exc_type
from pydantic.utils import Representation


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


def error_dict(
    exc: Exception, config: Type["BaseConfig"], loc: "Loc"
) -> Dict[str, Any]:
    type_ = get_exc_type(exc.__class__)
    msg_template = (
        config.error_msg_templates.get(f"{type_}.{'.'.join(map(str, loc))}")
        or config.error_msg_templates.get(type_)
        or getattr(exc, "msg_template", None)
    )
    ctx = exc.__dict__
    if msg_template:
        msg = msg_template.format(**ctx)
    else:
        msg = str(exc)

    d: Dict[str, Any] = {"loc": loc, "msg": msg, "type": type_}

    if ctx:
        d["ctx"] = ctx

    return d


class ErrorWrapper(Representation):
    __slots__ = "exc", "_loc"

    def __init__(self, exc: Exception, loc: Union[str, "Loc"]) -> None:
        if len(exc.args) > 1 and not isinstance(exc, pydantic.ValidationError):
            self.exc = exc.__class__(exc.args[0])
            self._loc = exc.args[1]
        else:
            self.exc = exc
            self._loc = loc

    def loc_tuple(self) -> "Loc":
        if isinstance(self._loc, tuple):
            return self._loc
        else:
            return (self._loc,)

    def __repr_args__(self) -> "ReprArgs":
        return [("exc", self.exc), ("loc", self.loc_tuple())]


pydantic.error_wrappers.ErrorWrapper = ErrorWrapper
pydantic.error_wrappers.ErrorList = Union[Sequence[Any], ErrorWrapper]
pydantic.main.ErrorWrapper = ErrorWrapper
pydantic.fields.ErrorWrapper = ErrorWrapper
pydantic.error_wrappers.error_dict = error_dict
pydantic.validators.enum_validator = enum_validator
# https://github.com/samuelcolvin/pydantic/blob/2eb62a3b2f/pydantic/validators.py#L500
pydantic.validators._VALIDATORS[0][1][1] = enum_validator
pydantic.validators._VALIDATORS[1][1][0] = enum_validator
