import querybuilder.query


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


querybuilder.query.Sorter = CompleteSorter
querybuilder.query.Query = Query
