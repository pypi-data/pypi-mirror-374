from typing import List, Optional, Self, Union
from dataclasses import dataclass
from abc import ABC
import datetime as dt
import uuid


type LQ = Union[None, int, float, bool, str, List[LQ]]


# raised when parsing user query
class QueryError(Exception): ...


class UnknownArgError(QueryError): ...


class UnknownFieldError(QueryError): ...


class QueryTypeError(QueryError): ...


class ContextNotSpecifiedError(QueryError): ...


class OverwriteContextError(QueryError): ...


# raised when creating context
class ContextError(Exception): ...


class ArgParserConflictError(ContextError): ...


class ContextFieldConflictError(ContextError): ...


class ContextTableConflictError(ContextError): ...


class ContextRootTableError(ContextError): ...


class ContextTableResolutionError(ContextError): ...


class InvalidAliasError(ContextError): ...


# raised when generating sql
class SqlGenError(Exception): ...


class MissingClaimsError(SqlGenError): ...


class ParamNameError(SqlGenError): ...


class MissingKeyFieldError(SqlGenError): ...


def validate_alias(alias: str):
    if len(alias) == 0:
        raise InvalidAliasError("empty alias")

    if alias[0] == "_":
        raise InvalidAliasError(f"alias cannot start with an underscore {alias=}")

    if alias[0].isdigit():
        raise InvalidAliasError(f"alias cannot start with a number {alias=}")

    for c in alias:
        if c == "_":
            continue

        if c.isalnum():
            continue

        raise InvalidAliasError(f"alias should be alphanumeric {alias=}")


class QueryType:
    numeric = "numeric"
    boolean = "boolean"
    text = "text"
    date = "date"
    uuid = "uuid"
    null = "null"
    condition = "condition"
    select = "select"
    update = "update"
    set = "set"
    insert = "insert"
    delete = "delete"
    where = "where"
    orderby = "orderby"
    direction = "direction"
    limit = "limit"
    offset = "offset"
    using = "using"

    value_types = {
        "numeric",
        "boolean",
        "text",
        "date",
        "uuid",
        "null",
    }


@dataclass
class ContextField:
    alias: str
    source: str
    query_type: str
    table_alias: str
    read_claim: str
    edit_claim: str
    filter_claim: str
    key: bool = False

    def __post_init__(self):
        validate_alias(self.alias)


@dataclass
class ContextTable:
    alias: str
    source: str
    join_condition: Optional[str]
    depends_on: list[str]

    def __post_init__(self):
        validate_alias(self.alias)


class Context:
    def __init__(
        self,
        tables: list[ContextTable],
        fields: list[ContextField],
        context_condition_sql: Optional[str] = None,
    ):
        self.context_condition_sql = context_condition_sql
        self.tables: dict[str, ContextTable] = dict()
        for t in tables:
            self._add_table(t)

        self.tables_order: list[str] = []
        self._set_tables_order()

        self.fields: dict[str, ContextField] = dict()
        for f in fields:
            self._add_field(f)

    def _add_field(self, field: ContextField):
        if field.alias in self.fields:
            raise ContextFieldConflictError(
                f"field.alias in self.fields {field.alias=}"
            )
        self.fields[field.alias] = field

    def _add_table(self, table: ContextTable):
        if table.alias in self.tables:
            raise ContextTableConflictError(
                f"table.alias in self.tables {table.alias=}"
            )

        self.tables[table.alias] = table

    def _set_tables_order(self):
        tables_order = []

        root_tables = {k for k, v in self.tables.items() if not v.depends_on}
        if len(root_tables) != 1:
            raise ContextRootTableError(f"len(root_tables) != 1 {root_tables=}")

        tables_order.append(list(root_tables)[0])
        remaining_tables = set(self.tables) - root_tables
        resolved_tables = set(root_tables)

        while len(remaining_tables) > 0:
            continue_resolve = False
            for table_alias in sorted(remaining_tables):
                table = self.tables[table_alias]
                depends_on = set(table.depends_on)
                if depends_on.issubset(resolved_tables):
                    tables_order.append(table_alias)
                    resolved_tables.add(table_alias)
                    remaining_tables.discard(table_alias)
                    continue_resolve = True
            if not continue_resolve:
                raise ContextTableResolutionError(
                    f"_set_tables_order {remaining_tables=} {resolved_tables=}"
                )

        self.tables_order = tables_order


class ContextRegistry(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

        # FIXME date_delta, union?
        self.arg_parsers = {
            "str": QueryStr,
            "date": QueryDate,
            "uuid": QueryUuid,
            "concat": QueryConcat,
            "lower": QueryLower,
            "upper": QueryUpper,
            "add": QueryAdd,
            "sub": QuerySub,
            "mul": QueryMul,
            "div": QueryDiv,
            "coalesce": QueryCoalesce,
            "select": QuerySelect,
            "where": QueryWhere,
            "and": QueryAnd,
            "or": QueryOr,
            "like": QueryLike,
            "eq": QueryEq,
            "neq": QueryNeq,
            "lt": QueryLt,
            "gt": QueryGt,
            "lte": QueryLte,
            "gte": QueryGte,
            "not": QueryNot,
            "is_null": QueryIsNull,
            "is_not_null": QueryIsNotNull,
            "in": QueryIn,
            "orderby": QueryOrderby,
            "asc": QueryAsc,
            "desc": QueryDesc,
            "limit": QueryLimit,
            "offset": QueryOffset,
            "update": QueryUpdate,
            "set": QuerySet,
            "insert": QueryInsert,
            "delete": QueryDelete,
            "using": QueryUsing,
            "query": Query,
        }

    def parse_query(self, lq: LQ):
        q = Query(lq=lq, context_registry=self)
        return q

    def to_sql(self, lq: LQ, claims=None, params=None):
        q = Query(lq=lq, context_registry=self)
        q.assert_claims(claims)
        return q.to_sql(params)

    def add_arg_parser(
        self,
        query_id,
        query_cls,
    ):
        if query_id in self.arg_parsers:
            raise ArgParserConflictError(f"query_id in self.arg_parsers {query_id}")

        self.arg_parsers[query_id] = query_cls


def find_context_alias(lq: LQ):
    if not isinstance(lq, list):
        return None

    lq = [q for q in lq if len(q) > 0 and q[0] == "using"]
    if len(lq) != 1:
        return None

    lq = lq[0]
    if len(lq) != 2:
        raise ContextNotSpecifiedError(f"{lq=}")

    context_alias = lq[1]
    if not isinstance(context_alias, str):
        raise ContextNotSpecifiedError(
            f"not isinstance(context_alias, str), {context_alias=}"
        )

    return context_alias


def parse_arg(
    *,
    lq: LQ,
    context: Optional[Context] = None,
    context_registry: Optional[ContextRegistry] = None,
):
    if lq is None:
        return QueryNull()
    elif isinstance(lq, float):
        return QueryFloat(lq)
    elif isinstance(lq, int):
        return QueryInt(lq)
    elif isinstance(lq, bool):
        return QueryBool(lq)
    elif isinstance(lq, str):
        return QueryField(context, lq)
    elif context_registry is None:
        raise ContextNotSpecifiedError(
            f"context_registry is needed to parse the argument {lq=}"
        )
    elif isinstance(lq, list):
        assert len(lq) > 0
        q_id = lq[0]
        arg = context_registry.arg_parsers[q_id](
            lq=lq, context=context, context_registry=context_registry
        )
        return arg
    else:
        raise UnknownArgError(f"parse_arg error {lq}")


def parse_args(
    *,
    lq: LQ,
    context: Optional[Context] = None,
    context_registry: Optional[ContextRegistry] = None,
):
    if lq is None:
        return QueryNull()
    result = [
        parse_arg(lq=a, context=context, context_registry=context_registry) for a in lq
    ]
    return result


def assert_args_types(args, allowed_types: set):
    for arg in args:
        arg_query_type = arg.query_type()
        if arg_query_type not in allowed_types:
            raise QueryTypeError(
                f"assert_args_types {arg=} {arg_query_type=} {allowed_types=}"
            )


def assert_args_types_equal(args):
    if len(args) < 2:
        return

    query_types = {a.query_type() for a in args}
    if len(query_types) > 1:
        raise QueryTypeError(f"assert_args_types_equal {query_types=}")


def assert_args_contains_exactly_1(args, target_types):
    found_types = [a.query_type() for a in args if a.query_type() in target_types]
    if len(found_types) != 1:
        raise QueryTypeError(f"assert_args_contains_exactly_1 {found_types=}")

    return list(found_types)[0]


def assert_args_contains_at_most_1(args, target_types):
    found_types = [a.query_type() for a in args if a.query_type() in target_types]
    if len(found_types) > 1:
        raise QueryTypeError(f"assert_args_contains_at_most_1 {found_types=}")


def find_arg_by_type(args, target_type):
    found = [a for a in args if a.query_type() == target_type]
    if len(found) > 1:
        raise QueryTypeError(f"find_arg_by_type more than one found {target_type=}")

    if len(found) == 0:
        return None

    return found[0]


def create_new_param(params, value):
    param_name = f"param_{len(params)}"
    if param_name in params:
        raise ParamNameError(f"create_new_param {param_name=}")
    params[param_name] = value
    return param_name, params


class QueryBase(ABC):
    args: list[Self] = []
    context: Optional[Context] = None

    def to_sql(self):
        raise NotImplementedError("to_sql")

    def query_type(self):
        raise NotImplementedError("query_type")

    def collect_fields(self):
        result = set()
        for arg in self.args:
            result |= arg.collect_fields()
        return result

    def collect_read_claims(self):
        result = set()
        for arg in self.args:
            result |= arg.collect_read_claims()
        return result

    def collect_filter_claims(self):
        result = set()
        for arg in self.args:
            result |= arg.collect_filter_claims()
        return result

    def collect_edit_claims(self):
        result = set()
        for arg in self.args:
            result |= arg.collect_edit_claims()
        return result

    def get_required_tables(self):
        fields = self.collect_fields()
        if len(fields) == 0:
            return set()
        if self.context is None:
            raise SqlGenError(f"self.context is None {fields=}")
        fields = [self.context.fields[f] for f in fields]
        tables = set()
        for field in fields:
            tables.add(field.table_alias)

        tables = [self.context.tables[t] for t in tables]
        required_tables = set()
        for table in tables:
            required_tables.add(table.alias)
            for table_alias in table.depends_on:
                required_tables.add(table_alias)

        return required_tables

    def build_from_clause(self, from_keyword="FROM", overwrite_root_table_source=None):
        required_tables = self.get_required_tables()
        if len(required_tables) == 0:
            return ""

        root_table = self.context.tables_order[0]
        root_table = self.context.tables[root_table]
        root_table_source = overwrite_root_table_source
        if root_table_source is None:
            root_table_source = root_table.source
        from_clause = f"{from_keyword} {root_table_source} {root_table.alias}"
        required_tables -= {root_table.alias}
        for table_alias in self.context.tables_order:
            if table_alias not in required_tables:
                continue

            table = self.context.tables[table_alias]
            from_clause += (
                f"\nLEFT JOIN {table.source} {table.alias} ON {table.join_condition}"
            )

        return from_clause

    def get_required_claims(self):
        result = set()
        result |= self.collect_read_claims()
        result |= self.collect_filter_claims()
        result |= self.collect_edit_claims()
        return result

    def assert_claims(self, claims=None):
        if claims is None:
            claims = set()

        claims = set(claims)
        required_claims = self.get_required_claims()
        missing_claims = required_claims - claims
        if len(missing_claims) == 0:
            return

        raise MissingClaimsError(f"assert_claims {missing_claims=}")


class QueryFloat(QueryBase):
    def __init__(self, lq_arg):
        assert isinstance(lq_arg, float)
        self.value = lq_arg

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        param_name, params = create_new_param(params, self.value)
        return f"%({param_name})s", params

    def query_type(self):
        return QueryType.numeric


class QueryInt(QueryBase):
    def __init__(self, lq_arg):
        assert isinstance(lq_arg, int)
        self.value = lq_arg

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        param_name, params = create_new_param(params, self.value)
        return f"%({param_name})s", params

    def query_type(self):
        return QueryType.numeric


class QueryBool(QueryBase):
    def __init__(self, lq_arg):
        assert isinstance(lq_arg, bool)
        self.value = lq_arg

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        if self.value:
            return "TRUE", params
        else:
            return "FALSE", params

    def query_type(self):
        return QueryType.boolean


class QueryNull(QueryBase):
    def __init__(self):
        pass

    def to_sql(self, params=None):
        if params is None:
            params = dict()
        return "NULL", params

    def query_type(self):
        return QueryType.null


class QueryStr(QueryBase):
    def __init__(
        self,
        *,
        lq: LQ,
        context: Optional[Context] = None,
        context_registry: Optional[ContextRegistry] = None,
    ):
        assert lq is not None
        assert len(lq) == 2
        assert lq[0] == "str"
        if isinstance(lq[1], str):
            self.value = lq[1]
        elif lq[1] is None:
            self.value = None
        else:
            # FIXME maybe ValueTypeError?
            raise QueryTypeError(f"expected type of str or None {lq=}")

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        param_name, params = create_new_param(params, self.value)
        return f"%({param_name})s", params

    def query_type(self):
        return QueryType.text


class QueryDate(QueryBase):
    def __init__(
        self,
        *,
        lq: LQ,
        context: Optional[Context] = None,
        context_registry: Optional[ContextRegistry] = None,
    ):
        assert lq is not None
        assert len(lq) == 2
        assert lq[0] == "date"
        if lq[1] is None:
            self.value = None
        elif isinstance(lq[1], str):
            self.value = dt.datetime.fromisoformat(lq[1])
        elif isinstance(lq[1], (int, float)):
            self.value = dt.datetime.fromtimestamp(lq[1], dt.timezone.utc)
        else:
            raise QueryTypeError(f"expected type of int, str or None {lq=}")

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        param_name, params = create_new_param(params, self.value)
        return f"%({param_name})s", params

    def query_type(self):
        return QueryType.date


class QueryUuid(QueryBase):
    def __init__(
        self,
        *,
        lq: LQ,
        context: Optional[Context] = None,
        context_registry: Optional[ContextRegistry] = None,
    ):
        assert lq is not None
        assert len(lq) == 2
        assert lq[0] == "uuid"
        if lq[1] is None:
            self.value = None
        elif isinstance(lq[1], str):
            self.value = uuid.UUID(lq[1])
        else:
            raise QueryTypeError(f"expected type of str or None {lq=}")

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        param_name, params = create_new_param(params, self.value)
        return f"%({param_name})s", params

    def query_type(self):
        return QueryType.uuid


class QuerySelect(QueryBase):
    def __init__(
        self,
        *,
        lq: LQ,
        context: Optional[Context] = None,
        context_registry: Optional[ContextRegistry] = None,
    ):
        assert lq is not None
        assert len(lq) > 1
        assert lq[0] == "select"

        lq_args = lq[1:]
        args = parse_args(
            lq=lq_args,
            context=context,
            context_registry=context_registry,
        )
        assert_args_types(
            args,
            QueryType.value_types,
        )
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        args_sql = [arg.to_sql(params)[0] for arg in self.args]
        return f"SELECT {', '.join(args_sql)}", params

    def to_sql_insert_data(self, aliases, params=None):
        assert len(self.args) == len(aliases)

        if params is None:
            params = dict()

        args_sql = [
            f"{arg.to_sql(params)[0]} AS {alias}"
            for arg, alias in zip(self.args, aliases)
        ]
        return f"SELECT {', '.join(args_sql)}", params

    def query_type(self):
        return QueryType.select

    def collect_edit_claims(self):
        return set()

    def collect_filter_claims(self):
        return set()


class QueryConcat(QueryBase):
    def __init__(
        self,
        *,
        lq: LQ,
        context: Optional[Context] = None,
        context_registry: Optional[ContextRegistry] = None,
    ):
        assert lq is not None
        assert len(lq) > 1
        assert lq[0] == "concat"
        lq_args = lq[1:]
        args = parse_args(
            lq=lq_args,
            context=context,
            context_registry=context_registry,
        )
        assert_args_types(
            args,
            {
                QueryType.text,
                QueryType.null,
            },
        )
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        args_sql = [arg.to_sql(params)[0] for arg in self.args]
        return f"({' || '.join(args_sql)})", params

    def query_type(self):
        return QueryType.text


class QueryLower(QueryBase):
    def __init__(
        self,
        *,
        lq: LQ,
        context: Optional[Context] = None,
        context_registry: Optional[ContextRegistry] = None,
    ):
        assert lq is not None
        assert len(lq) == 2
        assert lq[0] == "lower"
        lq_args = lq[1:]
        args = parse_args(
            lq=lq_args,
            context=context,
            context_registry=context_registry,
        )
        assert_args_types(
            args,
            {
                QueryType.text,
                QueryType.null,
            },
        )
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        sql_0, _ = self.args[0].to_sql(params)
        return f"LOWER({sql_0})", params

    def query_type(self):
        return QueryType.text


class QueryUpper(QueryBase):
    def __init__(
        self,
        *,
        lq: LQ,
        context: Optional[Context] = None,
        context_registry: Optional[ContextRegistry] = None,
    ):
        assert lq is not None
        assert len(lq) == 2
        assert lq[0] == "upper"
        lq_args = lq[1:]
        args = parse_args(
            lq=lq_args,
            context=context,
            context_registry=context_registry,
        )
        assert_args_types(
            args,
            {
                QueryType.text,
                QueryType.null,
            },
        )
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        sql_0, _ = self.args[0].to_sql(params)
        return f"UPPER({sql_0})", params

    def query_type(self):
        return QueryType.text


class QueryAdd(QueryBase):
    def __init__(
        self,
        *,
        lq: LQ,
        context: Optional[Context] = None,
        context_registry: Optional[ContextRegistry] = None,
    ):
        assert lq is not None
        assert len(lq) > 1
        assert lq[0] == "add"
        lq_args = lq[1:]
        args = parse_args(
            lq=lq_args,
            context=context,
            context_registry=context_registry,
        )
        assert_args_types(
            args,
            {
                QueryType.numeric,
                QueryType.null,
            },
        )
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        args_sql = [arg.to_sql(params)[0] for arg in self.args]
        return f"({' + '.join(args_sql)})", params

    def query_type(self):
        return QueryType.numeric


class QuerySub(QueryBase):
    def __init__(
        self,
        *,
        lq: LQ,
        context: Optional[Context] = None,
        context_registry: Optional[ContextRegistry] = None,
    ):
        assert lq is not None
        assert len(lq) > 1
        assert lq[0] == "sub"
        lq_args = lq[1:]
        args = parse_args(
            lq=lq_args,
            context=context,
            context_registry=context_registry,
        )
        assert_args_types(
            args,
            {
                QueryType.numeric,
                QueryType.null,
            },
        )
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        args_sql = [arg.to_sql(params)[0] for arg in self.args]
        return f"({' - '.join(args_sql)})", params

    def query_type(self):
        return QueryType.numeric


class QueryMul(QueryBase):
    def __init__(
        self,
        *,
        lq: LQ,
        context: Optional[Context] = None,
        context_registry: Optional[ContextRegistry] = None,
    ):
        assert lq is not None
        assert len(lq) > 1
        assert lq[0] == "mul"
        lq_args = lq[1:]
        args = parse_args(
            lq=lq_args,
            context=context,
            context_registry=context_registry,
        )
        assert_args_types(
            args,
            {
                QueryType.numeric,
                QueryType.null,
            },
        )
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        args_sql = [arg.to_sql(params)[0] for arg in self.args]
        return f"({' * '.join(args_sql)})", params

    def query_type(self):
        return QueryType.numeric


class QueryDiv(QueryBase):
    def __init__(
        self,
        *,
        lq: LQ,
        context: Optional[Context] = None,
        context_registry: Optional[ContextRegistry] = None,
    ):
        assert lq is not None
        assert len(lq) == 3
        assert lq[0] == "div"
        lq_args = lq[1:]
        args = parse_args(
            lq=lq_args,
            context=context,
            context_registry=context_registry,
        )
        assert_args_types(
            args,
            {
                QueryType.numeric,
                QueryType.null,
            },
        )
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        args_sql = [arg.to_sql(params)[0] for arg in self.args]
        return f"({' / '.join(args_sql)})", params

    def query_type(self):
        return QueryType.numeric


class QueryField(QueryBase):
    def __init__(self, context: Context, lq_arg: LQ):
        if context is None:
            raise UnknownFieldError(f"context is None {lq_arg=}")
        if lq_arg not in context.fields:
            raise UnknownFieldError(f"lq_arg not in context.fields {lq_arg=}")

        context_field = context.fields[lq_arg]
        self.table_alias = context_field.table_alias
        self.source = context_field.source
        self.alias = lq_arg
        self.field_query_type = context.fields[lq_arg].query_type
        self.context: Context = context

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        return f"{self.table_alias}.{self.source}", params

    def query_type(self):
        return self.field_query_type

    def collect_fields(self):
        return set([self.alias])

    def collect_read_claims(self):
        field = self.context.fields[self.alias]
        if field.read_claim:
            return set([field.read_claim])
        return set()

    def collect_filter_claims(self):
        field = self.context.fields[self.alias]
        if field.filter_claim:
            return set([field.filter_claim])
        return set()

    def collect_edit_claims(self):
        field = self.context.fields[self.alias]
        if field.edit_claim:
            return set([field.edit_claim])
        return set()


class QueryCoalesce(QueryBase):
    def __init__(
        self,
        *,
        lq: LQ,
        context: Optional[Context] = None,
        context_registry: Optional[ContextRegistry] = None,
    ):
        assert lq is not None
        assert len(lq) >= 2
        assert lq[0] == "coalesce"
        lq_args = lq[1:]
        args = parse_args(
            lq=lq_args,
            context=context,
            context_registry=context_registry,
        )
        assert_args_types(args, QueryType.value_types)
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        args_sql = [arg.to_sql(params)[0] for arg in self.args]
        return f"COALESCE({", ".join(args_sql)})", params

    def query_type(self):
        return self.args[0].query_type()


class QueryWhere(QueryBase):
    def __init__(
        self,
        *,
        lq: LQ,
        context: Optional[Context] = None,
        context_registry: Optional[ContextRegistry] = None,
    ):
        assert lq is not None
        assert len(lq) >= 1
        assert lq[0] == "where"

        self.context_condition_sql = None
        if context is not None:
            self.context_condition_sql = context.context_condition_sql

        if len(lq) == 1:
            self.args = []
            return

        lq_args = lq[1:]
        args = parse_args(
            lq=lq_args,
            context=context,
            context_registry=context_registry,
        )
        assert_args_types(
            args,
            {QueryType.condition},
        )
        self.args = args

    def to_sql(self, params=None, extra_condition_sql=None):
        if params is None:
            params = dict()

        # Act as AND operator to make easy to add query constraints on backend
        args_sql = [arg.to_sql(params)[0] for arg in self.args]
        if self.context_condition_sql is not None:
            args_sql.append(self.context_condition_sql)

        if extra_condition_sql is not None:
            args_sql.append(extra_condition_sql)

        if len(args_sql) == 0:
            return "", params

        return f"WHERE ({' AND '.join(args_sql)})", params

    def query_type(self):
        return QueryType.where

    def collect_edit_claims(self):
        return set()

    def add_condition(
        self,
        *,
        lq: LQ,
        context: Optional[Context] = None,
        context_registry: Optional[ContextRegistry] = None,
    ):
        lq_args = [lq]
        args = parse_args(
            lq=lq_args,
            context=context,
            context_registry=context_registry,
        )
        assert_args_types(
            args,
            {QueryType.condition},
        )
        self.args.extend(args)


class QueryAnd(QueryBase):
    def __init__(
        self,
        *,
        lq: LQ,
        context: Optional[Context] = None,
        context_registry: Optional[ContextRegistry] = None,
    ):
        assert lq is not None
        assert len(lq) > 1
        assert lq[0] == "and"

        lq_args = lq[1:]
        args = parse_args(
            lq=lq_args,
            context=context,
            context_registry=context_registry,
        )
        assert_args_types(args, {QueryType.condition})
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        args_sql = [arg.to_sql(params)[0] for arg in self.args]
        return f"({' AND '.join(args_sql)})", params

    def query_type(self):
        return QueryType.condition


class QueryOr(QueryBase):
    def __init__(
        self,
        *,
        lq: LQ,
        context: Optional[Context] = None,
        context_registry: Optional[ContextRegistry] = None,
    ):
        assert lq is not None
        assert len(lq) > 1
        assert lq[0] == "or"

        lq_args = lq[1:]
        args = parse_args(
            lq=lq_args,
            context=context,
            context_registry=context_registry,
        )
        assert_args_types(args, {QueryType.condition})
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        args_sql = [arg.to_sql(params)[0] for arg in self.args]
        return f"({' OR '.join(args_sql)})", params

    def query_type(self):
        return QueryType.condition


class QueryEq(QueryBase):
    def __init__(
        self,
        *,
        lq: LQ,
        context: Optional[Context] = None,
        context_registry: Optional[ContextRegistry] = None,
    ):
        assert lq is not None
        assert len(lq) == 3
        assert lq[0] == "eq"

        lq_args = lq[1:]
        args = parse_args(
            lq=lq_args,
            context=context,
            context_registry=context_registry,
        )
        assert_args_types(args, QueryType.value_types)
        assert_args_types_equal(args)
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        sql_0, _ = self.args[0].to_sql(params)
        sql_1, _ = self.args[1].to_sql(params)
        return f"({sql_0} = {sql_1})", params

    def query_type(self):
        return QueryType.condition


class QueryNeq(QueryBase):
    def __init__(
        self,
        *,
        lq: LQ,
        context: Optional[Context] = None,
        context_registry: Optional[ContextRegistry] = None,
    ):
        assert lq is not None
        assert len(lq) == 3
        assert lq[0] == "neq"

        lq_args = lq[1:]
        args = parse_args(
            lq=lq_args,
            context=context,
            context_registry=context_registry,
        )
        assert_args_types(args, QueryType.value_types)
        assert_args_types_equal(args)
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        sql_0, _ = self.args[0].to_sql(params)
        sql_1, _ = self.args[1].to_sql(params)
        return f"({sql_0} != {sql_1})", params

    def query_type(self):
        return QueryType.condition


class QueryLt(QueryBase):
    def __init__(
        self,
        *,
        lq: LQ,
        context: Optional[Context] = None,
        context_registry: Optional[ContextRegistry] = None,
    ):
        assert lq is not None
        assert len(lq) == 3
        assert lq[0] == "lt"

        lq_args = lq[1:]
        args = parse_args(
            lq=lq_args,
            context=context,
            context_registry=context_registry,
        )
        assert_args_types(args, {QueryType.numeric, QueryType.null})
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        sql_0, _ = self.args[0].to_sql(params)
        sql_1, _ = self.args[1].to_sql(params)
        return f"({sql_0} < {sql_1})", params

    def query_type(self):
        return QueryType.condition


class QueryLte(QueryBase):
    def __init__(
        self,
        *,
        lq: LQ,
        context: Optional[Context] = None,
        context_registry: Optional[ContextRegistry] = None,
    ):
        assert lq is not None
        assert len(lq) == 3
        assert lq[0] == "lte"

        lq_args = lq[1:]
        args = parse_args(
            lq=lq_args,
            context=context,
            context_registry=context_registry,
        )
        assert_args_types(args, {QueryType.numeric, QueryType.null})
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        sql_0, _ = self.args[0].to_sql(params)
        sql_1, _ = self.args[1].to_sql(params)
        return f"({sql_0} <= {sql_1})", params

    def query_type(self):
        return QueryType.condition


class QueryGt(QueryBase):
    def __init__(
        self,
        *,
        lq: LQ,
        context: Optional[Context] = None,
        context_registry: Optional[ContextRegistry] = None,
    ):
        assert lq is not None
        assert len(lq) == 3
        assert lq[0] == "gt"

        lq_args = lq[1:]
        args = parse_args(
            lq=lq_args,
            context=context,
            context_registry=context_registry,
        )
        assert_args_types(args, {QueryType.numeric, QueryType.null})
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        sql_0, _ = self.args[0].to_sql(params)
        sql_1, _ = self.args[1].to_sql(params)
        return f"({sql_0} > {sql_1})", params

    def query_type(self):
        return QueryType.condition


class QueryGte(QueryBase):
    def __init__(
        self,
        *,
        lq: LQ,
        context: Optional[Context] = None,
        context_registry: Optional[ContextRegistry] = None,
    ):
        assert lq is not None
        assert len(lq) == 3
        assert lq[0] == "gte"

        lq_args = lq[1:]
        args = parse_args(
            lq=lq_args,
            context=context,
            context_registry=context_registry,
        )
        assert_args_types(args, {QueryType.numeric, QueryType.null})
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        sql_0, _ = self.args[0].to_sql(params)
        sql_1, _ = self.args[1].to_sql(params)
        return f"({sql_0} >= {sql_1})", params

    def query_type(self):
        return QueryType.condition


class QueryNot(QueryBase):
    def __init__(
        self,
        *,
        lq: LQ,
        context: Optional[Context] = None,
        context_registry: Optional[ContextRegistry] = None,
    ):
        assert lq is not None
        assert len(lq) == 2
        assert lq[0] == "not"

        lq_args = lq[1:]
        args = parse_args(
            lq=lq_args,
            context=context,
            context_registry=context_registry,
        )
        assert_args_types(args, {QueryType.condition})
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        sql_0, _ = self.args[0].to_sql(params)
        return f"(NOT {sql_0})", params

    def query_type(self):
        return QueryType.condition


class QueryIsNull(QueryBase):
    def __init__(
        self,
        *,
        lq: LQ,
        context: Optional[Context] = None,
        context_registry: Optional[ContextRegistry] = None,
    ):
        assert lq is not None
        assert len(lq) == 2
        assert lq[0] == "is_null"

        lq_args = lq[1:]
        args = parse_args(
            lq=lq_args,
            context=context,
            context_registry=context_registry,
        )
        assert_args_types(args, QueryType.value_types)
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        sql_0, _ = self.args[0].to_sql(params)
        return f"({sql_0} IS NULL)", params

    def query_type(self):
        return QueryType.condition


class QueryIsNotNull(QueryBase):
    def __init__(
        self,
        *,
        lq: LQ,
        context: Optional[Context] = None,
        context_registry: Optional[ContextRegistry] = None,
    ):
        assert lq is not None
        assert len(lq) == 2
        assert lq[0] == "is_not_null"

        lq_args = lq[1:]
        args = parse_args(
            lq=lq_args,
            context=context,
            context_registry=context_registry,
        )
        assert_args_types(args, QueryType.value_types)
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        sql_0, _ = self.args[0].to_sql(params)
        return f"({sql_0} IS NOT NULL)", params

    def query_type(self):
        return QueryType.condition


class QueryIn(QueryBase):
    def __init__(
        self,
        *,
        lq: LQ,
        context: Optional[Context] = None,
        context_registry: Optional[ContextRegistry] = None,
    ):
        assert lq is not None
        assert len(lq) >= 3
        assert lq[0] == "in"

        lq_args = lq[1:]
        args = parse_args(
            lq=lq_args,
            context=context,
            context_registry=context_registry,
        )
        assert_args_types(args, QueryType.value_types)
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        sql_0, _ = self.args[0].to_sql(params)
        sql_rest = [arg.to_sql(params)[0] for arg in self.args[1:]]
        return f"({sql_0} IN ({', '.join(sql_rest)}))", params

    def query_type(self):
        return QueryType.condition


class QueryLike(QueryBase):
    def __init__(
        self,
        *,
        lq: LQ,
        context: Optional[Context] = None,
        context_registry: Optional[ContextRegistry] = None,
    ):
        assert lq is not None
        assert len(lq) == 3
        assert lq[0] == "like"

        lq_args = lq[1:]
        args = parse_args(
            lq=lq_args,
            context=context,
            context_registry=context_registry,
        )
        assert_args_types(args, {QueryType.text, QueryType.null})
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        sql_0, _ = self.args[0].to_sql(params)
        sql_1, _ = self.args[1].to_sql(params)
        return f"({sql_0} LIKE {sql_1})", params

    def query_type(self):
        return QueryType.condition


class QueryOrderby(QueryBase):
    def __init__(
        self,
        *,
        lq: LQ,
        context: Optional[Context] = None,
        context_registry: Optional[ContextRegistry] = None,
    ):
        assert lq is not None
        assert len(lq) >= 1
        assert lq[0] == "orderby"

        if len(lq) == 1:
            self.args = []
            return

        lq_args = lq[1:]
        args = parse_args(
            lq=lq_args,
            context=context,
            context_registry=context_registry,
        )
        assert_args_types(args, QueryType.value_types | {QueryType.direction})
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        if len(self.args) == 0:
            return ""

        args_sql = [arg.to_sql(params)[0] for arg in self.args]
        return f"ORDER BY {', '.join(args_sql)}", params

    def query_type(self):
        return QueryType.orderby

    def collect_edit_claims(self):
        return set()


class QueryAsc(QueryBase):
    def __init__(
        self,
        *,
        lq: LQ,
        context: Optional[Context] = None,
        context_registry: Optional[ContextRegistry] = None,
    ):
        assert lq is not None
        assert len(lq) == 2
        assert lq[0] == "asc"

        lq_args = lq[1:]
        args = parse_args(
            lq=lq_args,
            context=context,
            context_registry=context_registry,
        )
        assert_args_types(args, QueryType.value_types)
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        sql_0, _ = self.args[0].to_sql(params)
        return f"{sql_0} ASC", params

    def query_type(self):
        return QueryType.direction


class QueryDesc(QueryBase):
    def __init__(
        self,
        *,
        lq: LQ,
        context: Optional[Context] = None,
        context_registry: Optional[ContextRegistry] = None,
    ):
        assert lq is not None
        assert len(lq) == 2
        assert lq[0] == "desc"

        lq_args = lq[1:]
        args = parse_args(
            lq=lq_args,
            context=context,
            context_registry=context_registry,
        )
        assert_args_types(args, QueryType.value_types)
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        sql_0, _ = self.args[0].to_sql(params)
        return f"{sql_0} DESC", params

    def query_type(self):
        return QueryType.direction


class QueryLimit(QueryBase):
    def __init__(
        self,
        *,
        lq: LQ,
        context: Optional[Context] = None,
        context_registry: Optional[ContextRegistry] = None,
    ):
        assert lq is not None
        assert len(lq) == 2
        assert lq[0] == "limit"

        lq_args = lq[1:]
        args = parse_args(
            lq=lq_args,
            context=context,
            context_registry=context_registry,
        )
        assert isinstance(args[0], QueryInt)
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        if len(self.args) == 0:
            return ""

        sql_0, _ = self.args[0].to_sql(params)
        return f"LIMIT {sql_0}", params

    def query_type(self):
        return QueryType.limit

    def collect_edit_claims(self):
        return set()


class QueryOffset(QueryBase):
    def __init__(
        self,
        *,
        lq: LQ,
        context: Optional[Context] = None,
        context_registry: Optional[ContextRegistry] = None,
    ):
        assert lq is not None
        assert len(lq) == 2
        assert lq[0] == "offset"

        lq_args = lq[1:]
        args = parse_args(
            lq=lq_args,
            context=context,
            context_registry=context_registry,
        )
        assert isinstance(args[0], QueryInt)
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        if len(self.args) == 0:
            return ""

        sql_0, _ = self.args[0].to_sql(params)
        return f"OFFSET {sql_0}", params

    def query_type(self):
        return QueryType.offset

    def collect_edit_claims(self):
        return set()


class QueryUpdate(QueryBase):
    def __init__(
        self,
        *,
        lq: LQ,
        context: Optional[Context] = None,
        context_registry: Optional[ContextRegistry] = None,
    ):
        assert lq is not None
        assert len(lq) >= 2
        assert lq[0] == "update"

        lq_args = lq[1:]
        args = parse_args(
            lq=lq_args,
            context=context,
            context_registry=context_registry,
        )
        assert_args_types(args, {QueryType.set})
        self.args = args
        self.context = context

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        root_table_alias = self.context.tables_order[0]
        update_table_alias = f"_{root_table_alias}_update"
        root_table = self.context.tables[root_table_alias]
        args_sql = [arg.to_sql(params)[0] for arg in self.args]
        return (
            f"UPDATE {root_table.source} {update_table_alias} SET {", ".join(args_sql)} ",
            params,
        )

    def query_type(self):
        return QueryType.update

    def get_self_join_sql(self):
        root_table_alias = self.context.tables_order[0]
        update_table_alias = f"_{root_table_alias}_update"
        key_fields = [f for f in self.context.fields.values() if f.key]
        if len(key_fields) == 0:
            raise MissingKeyFieldError(
                "at least one key field is required for update query"
            )

        conditions = []
        for field in sorted(key_fields, key=lambda f: f.alias):
            condition = f"{update_table_alias}.{field.source} = {root_table_alias}.{field.source}"
            conditions.append(condition)

        sql = f"({" AND ".join(conditions)})"
        return sql


class QuerySet(QueryBase):
    def __init__(
        self,
        *,
        lq: LQ,
        context: Optional[Context] = None,
        context_registry: Optional[ContextRegistry] = None,
    ):
        assert lq is not None
        assert len(lq) == 3
        assert lq[0] == "set"

        lq_arg_0 = lq[1]
        arg_0 = parse_arg(lq=lq_arg_0, context=context)
        if not isinstance(arg_0, QueryField):
            raise QueryTypeError(f"not isinstance(arg_0, QueryField) {lq=}")

        table_alias = arg_0.table_alias
        root_table_alias = context.tables_order[0]
        if table_alias != root_table_alias:
            raise QueryError(f"updating non root table {lq=}, {root_table_alias=}")

        lq_arg_1 = lq[2]
        arg_1 = parse_arg(lq=lq_arg_1, context=context)
        assert_args_types([arg_1], QueryType.value_types)
        assert_args_types_equal([arg_0, arg_1])

        self.arg_0: QueryField = arg_0
        self.arg_1: QueryBase = arg_1
        self.args = [arg_0, arg_1]

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        sql_0 = self.arg_0.source
        sql_1, _ = self.arg_1.to_sql(params)

        return f"{sql_0} = {sql_1}", params

    def query_type(self):
        return QueryType.set

    def collect_read_claims(self):
        return self.arg_1.collect_read_claims()

    def collect_filter_claims(self):
        return set()

    def collect_edit_claims(self):
        return self.arg_0.collect_edit_claims()


class QueryInsert(QueryBase):
    def __init__(
        self,
        *,
        lq: LQ,
        context: Optional[Context] = None,
        context_registry: Optional[ContextRegistry] = None,
    ):
        assert lq is not None
        assert len(lq) >= 3
        assert lq[0] == "insert"
        context_alias = lq[1]
        assert isinstance(context_alias, str)
        context = context_registry.get(context_alias)
        assert context is not None

        lq_args = lq[2:]
        args = parse_args(
            lq=lq_args,
            context=context,
            context_registry=context_registry,
        )

        root_table_alias = context.tables_order[0]
        for arg in args:
            if not isinstance(arg, QueryField):
                raise QueryTypeError(
                    """should be ["insert", <context_alias>, ...<context_fields>]"""
                )
            if arg.table_alias != root_table_alias:
                raise QueryTypeError("inserting into non root table is not allowed")

        self.args = args
        self.context: Context = context
        self.where = QueryWhere(
            lq=["where"],
            context=context,
            context_registry=context_registry,
        )

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        root_table_alias = self.context.tables_order[0]
        root_table = self.context.tables[root_table_alias]
        args_sql = [arg.source for arg in self.args]
        sql = f"INSERT INTO {root_table.source} ({", ".join(args_sql)})"
        return sql, params

    def query_type(self):
        return QueryType.insert

    def collect_fields(self):
        return set()

    def collect_read_claims(self):
        return set()

    def collect_filter_claims(self):
        return set()

    def collect_edit_claims(self):
        result = set()
        root_table_alias = self.context.tables_order[0]
        for field in self.context.fields.values():
            if field.table_alias != root_table_alias:
                continue
            if field.edit_claim is not None:
                result.add(field.edit_claim)

        return result

    def get_required_tables(self):
        root_table_alias = self.context.tables_order[0]
        required_tables = super().get_required_tables()
        required_tables.add(root_table_alias)
        return required_tables


class QueryDelete(QueryBase):
    def __init__(
        self,
        *,
        lq: LQ,
        context: Optional[Context] = None,
        context_registry: Optional[ContextRegistry] = None,
    ):
        assert lq is not None
        assert len(lq) == 1
        assert lq[0] == "delete"
        assert context is not None
        self.args = []
        self.context: Context = context

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        root_table_alias = self.context.tables_order[0]
        delete_table_alias = f"_{root_table_alias}_delete"
        root_table = self.context.tables[root_table_alias]
        return (
            f"DELETE FROM {root_table.source} {delete_table_alias}",
            params,
        )

    def query_type(self):
        return QueryType.delete

    def collect_edit_claims(self):
        result = set()
        root_table_alias = self.context.tables_order[0]
        for field in self.context.fields.values():
            if field.table_alias != root_table_alias:
                continue
            if field.edit_claim is not None:
                result.add(field.edit_claim)

        return result

    def get_self_join_sql(self):
        root_table_alias = self.context.tables_order[0]
        delete_table_alias = f"_{root_table_alias}_delete"
        key_fields = [f for f in self.context.fields.values() if f.key]
        if len(key_fields) == 0:
            raise MissingKeyFieldError(
                "at least one key field is required for delete query"
            )

        conditions = []
        for field in sorted(key_fields, key=lambda f: f.alias):
            condition = f"{delete_table_alias}.{field.source} = {root_table_alias}.{field.source}"
            conditions.append(condition)

        sql = f"({" AND ".join(conditions)})"
        return sql


class QueryUsing(QueryBase):
    def __init__(
        self,
        *,
        lq: LQ,
        context: Optional[Context] = None,
        context_registry: Optional[ContextRegistry] = None,
    ):
        assert lq is not None
        assert len(lq) == 2
        assert lq[0] == "using"
        assert isinstance(lq[1], str)
        self.context_alias = lq[1]

    def query_type(self):
        return QueryType.using


class Query(QueryBase):
    def __init__(
        self,
        *,
        lq: LQ,
        context: Optional[Context] = None,
        context_registry: Optional[ContextRegistry] = None,
    ):
        assert lq is not None

        context_alias = find_context_alias(lq)
        if context_alias is not None and context is not None:
            raise OverwriteContextError(
                f"Context alias should not be specified {context_alias=}"
            )

        if context is None:
            if context_alias is not None:
                context = context_registry.get(context_alias)

        self.context = context

        args = parse_args(
            lq=lq,
            context=context,
            context_registry=context_registry,
        )

        self.select: Optional[QuerySelect] = find_arg_by_type(args, QueryType.select)
        self.update: Optional[QueryUpdate] = find_arg_by_type(args, QueryType.update)
        self.insert: Optional[QueryInsert] = find_arg_by_type(args, QueryType.insert)
        self.delete: Optional[QueryDelete] = find_arg_by_type(args, QueryType.delete)
        self.where: Optional[QueryWhere] = find_arg_by_type(args, QueryType.where)
        if self.where is None:
            self.where = QueryWhere(
                lq=["where"],
                context=context,
                context_registry=context_registry,
            )
            args.append(self.where)
        self.orderby: Optional[QueryOrderby] = find_arg_by_type(args, QueryType.orderby)
        self.limit: Optional[QueryLimit] = find_arg_by_type(args, QueryType.limit)
        self.offset: Optional[QueryOffset] = find_arg_by_type(args, QueryType.offset)
        self.args = args

        if self.insert is not None:
            if self.select is None:
                raise QueryTypeError("select is required for insert query")
            if self.update is not None:
                raise QueryTypeError("update in insert query")
            if self.delete is not None:
                raise QueryTypeError("delete in insert query")

            insert_table_alias = self.insert.context.tables_order[0]

            self.insert: QueryInsert
            self.select: QuerySelect
            if len(self.insert.args) != len(self.select.args):
                raise QueryTypeError("len(self.insert.args) != len(self.select.args)")
            for select_arg, insert_arg in zip(self.select.args, self.insert.args):
                if not isinstance(insert_arg, QueryField):
                    raise QueryTypeError("not isinstance(insert_arg, QueryField)")

                insert_field_alias = insert_arg.alias
                insert_field = self.insert.context.fields[insert_field_alias]
                if insert_field.table_alias != insert_table_alias:
                    raise QueryTypeError(
                        "insert_field.table_alias != insert_table_alias"
                    )

                if select_arg.query_type() != insert_arg.query_type():
                    raise QueryTypeError(
                        "select_arg.query_type() != insert_arg.query_type()"
                    )

        elif self.select is not None:
            if self.update is not None:
                raise QueryTypeError("update in select query")
            if self.delete is not None:
                raise QueryTypeError("delete in select query")

        elif self.update is not None:
            if self.delete is not None:
                raise QueryTypeError("delete in update query")

        elif self.delete is not None:
            if self.orderby is not None:
                raise QueryTypeError("orderby in delete query")
            if self.limit is not None:
                raise QueryTypeError("limit in delete query")
            if self.offset is not None:
                raise QueryTypeError("offset in delete query")

        else:
            raise QueryTypeError(
                "query should be one of 'insert', 'select', 'update' or 'delete'"
            )

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        if self.insert is not None:
            insert_data_aliases = [a.alias for a in self.insert.args]

            insert_data_select_part, _ = self.select.to_sql_insert_data(
                insert_data_aliases,
                params,
            )
            insert_data_from_part = self.build_from_clause()
            insert_data_where_part = ""
            if self.where is not None:
                insert_data_where_part, _ = self.where.to_sql(params)
            insert_data_orderby_part = ""
            if self.orderby is not None:
                insert_data_orderby_part, _ = self.orderby.to_sql(params)
            insert_data_limit_part = ""
            if self.limit is not None:
                insert_data_limit_part, _ = self.limit.to_sql(params)
            insert_data_offset_part = ""
            if self.offset is not None:
                insert_data_offset_part, _ = self.offset.to_sql(params)

            insert_data_parts = [
                insert_data_select_part,
                insert_data_from_part,
                insert_data_where_part,
                insert_data_orderby_part,
                insert_data_limit_part,
                insert_data_offset_part,
            ]
            insert_data_parts = [p for p in insert_data_parts if p]
            insert_data_part = f"WITH _insert_data AS ( {"\n".join(insert_data_parts)} )"

            insert_part, _ = self.insert.to_sql(params)
            select_part = "SELECT *"
            from_part = self.insert.build_from_clause(
                overwrite_root_table_source="_insert_data",
            )
            where_part, _ = self.insert.where.to_sql(params)

            parts = [
                insert_data_part,
                insert_part,
                select_part,
                from_part,
                where_part,
            ]
            parts = [p for p in parts if p]
            return "\n".join(parts) + ";", params
        elif self.select is not None:
            select_part, _ = self.select.to_sql(params)
            where_part = ""
            if self.where is not None:
                where_part, _ = self.where.to_sql(params)
            orderby_part = ""
            if self.orderby is not None:
                orderby_part, _ = self.orderby.to_sql(params)
            limit_part = ""
            if self.limit is not None:
                limit_part, _ = self.limit.to_sql(params)
            offset_part = ""
            if self.offset is not None:
                offset_part, _ = self.offset.to_sql(params)
            from_part = self.build_from_clause()
            parts = [
                select_part,
                from_part,
                where_part,
                orderby_part,
                limit_part,
                offset_part,
            ]
            parts = [p for p in parts if p]
            return "\n".join(parts) + ";", params
        elif self.update is not None:
            update_part, _ = self.update.to_sql(params)
            self_join_sql = self.update.get_self_join_sql()
            q_where = self.where
            if q_where is None:
                q_where = QueryWhere(lq=["where"], context=self.context)
            where_part, _ = q_where.to_sql(params, extra_condition_sql=self_join_sql)
            orderby_part = ""
            if self.orderby is not None:
                orderby_part, _ = self.orderby.to_sql(params)
            limit_part = ""
            if self.limit is not None:
                limit_part, _ = self.limit.to_sql(params)
            offset_part = ""
            if self.offset is not None:
                offset_part, _ = self.offset.to_sql(params)
            from_part = self.build_from_clause()
            parts = [
                update_part,
                from_part,
                where_part,
                orderby_part,
                limit_part,
                offset_part,
            ]
            parts = [p for p in parts if p]
            return "\n".join(parts) + ";", params
        elif self.delete is not None:
            delete_part, _ = self.delete.to_sql(params)
            self_join_sql = self.delete.get_self_join_sql()
            q_where = self.where
            if q_where is None:
                q_where = QueryWhere(lq=["where"], context=self.context)
            where_part, _ = q_where.to_sql(params, extra_condition_sql=self_join_sql)
            from_part = self.build_from_clause(from_keyword="USING")
            parts = [
                delete_part,
                from_part,
                where_part,
            ]
            parts = [p for p in parts if p]
            return "\n".join(parts) + ";", params

        else:
            raise Exception("unexpected query")

    def add_where_condition(self, lq):
        if self.where is None:
            arg = QueryWhere(lq=["where"], context=self.context)
            self.where = arg
            self.args.append(arg)

        self.where.add_condition(self.context, lq)

    def set_limit(self, limit):
        self.args = [a for a in self.args if a.query_type() != QueryType.limit]
        arg = QueryLimit(self.context, ["limit", limit])
        self.limit = arg
        self.args.append(arg)

    def set_offset(self, offset):
        self.args = [a for a in self.args if a.query_type() != QueryType.offset]
        arg = QueryOffset(self.context, ["offset", offset])
        self.offset = arg
        self.args.append(arg)
