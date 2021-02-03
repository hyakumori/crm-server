import io
import logging

from itertools import chain

from django.core.cache import cache
from django.http import JsonResponse, HttpResponseBadRequest

from hyakumori_crm.crm.restful.paginations import StandardPagination


def get_remote_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        remote_ip = x_forwarded_for.split(",")[0]
    else:
        remote_ip = request.META.get("REMOTE_ADDR")

    return remote_ip


def model_to_dict(instance, fields=None, exclude=None):
    """
    Copy from django.form.models
    Tweak to remove ``editable`` conditions, by default return all infos
    ----------
    Return a dict containing the data in ``instance`` suitable for passing as
    a Form's ``initial`` keyword argument.

    ``fields`` is an optional list of field names. If provided, return only the
    named.

    ``exclude`` is an optional list of field names. If provided, exclude the
    named from the returned dict, even if they are listed in the ``fields``
    argument.
    """
    opts = instance._meta
    data = {}
    for f in chain(opts.concrete_fields, opts.private_fields, opts.many_to_many):
        if fields is not None and f.name not in fields:
            continue
        if exclude and f.name in exclude:
            continue
        data[f.name] = f.value_from_object(instance)
    return data


def default_paginator():
    paginator = StandardPagination()

    return paginator


def make_error_json(message: str, status=HttpResponseBadRequest.status_code):
    return JsonResponse(status=status, data=dict(detail=message))


def make_success_json(data: any):
    return JsonResponse(data=data)


class SQLFormatter(logging.Formatter):
    def format(self, record):
        # Check if Pygments is available for coloring
        try:
            import pygments
            from pygments.lexers import SqlLexer
            from pygments.formatters import TerminalTrueColorFormatter
        except ImportError:
            pygments = None

        # Check if sqlparse is available for indentation
        try:
            import sqlparse
        except ImportError:
            sqlparse = None

        # Remove leading and trailing whitespaces
        sql = record.sql.strip()

        if sqlparse:
            # Indent the SQL query
            sql = sqlparse.format(sql, reindent=True)

        if pygments:
            # Highlight the SQL query
            sql = pygments.highlight(
                sql, SqlLexer(), TerminalTrueColorFormatter(style="monokai")
            )

        # Set the record's statement to the formatted query
        record.statement = sql
        return super(SQLFormatter, self).format(record)


class Echo:
    """An object that implements just the write method of the file-like
    interface.
    """

    def __init__(self, initial_content=""):
        self.initial_content = io.StringIO(initial_content)

    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return self.initial_content.read() + value


def clear_maintain_task_id_cache(task=None):
    cache.delete("maintain_task_id")
