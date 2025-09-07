from sqlalchemy import asc, desc, or_
from sqlalchemy.sql.sqltypes import (
    String, Text, Integer, BigInteger, SmallInteger, Numeric, Float, Boolean, Enum as SAEnum
)
from sqlalchemy.orm import Session, Query
from sqlalchemy.dialects.postgresql import ENUM as PGEnum

from nlbone.interfaces.api.exceptions import UnprocessableEntityException
from nlbone.interfaces.api.pagination import PaginateRequest

NULL_SENTINELS = {"None", "null", ""}


class _InvalidEnum(Exception):
    pass


def _apply_order(pagination, entity, query):
    if pagination.sort:
        order_clauses = []
        for sort in pagination.sort:
            field = sort["field"]
            order = sort["order"]

            if hasattr(entity, field):
                column = getattr(entity, field)
                if order == "asc":
                    order_clauses.append(asc(column))
                else:
                    order_clauses.append(desc(column))

        if order_clauses:
            query = query.order_by(*order_clauses)
    return query


def _coerce_enum(col_type, raw):
    if raw is None:
        return None
    enum_cls = getattr(col_type, "enum_class", None)
    if enum_cls is not None:
        if isinstance(raw, enum_cls):
            return raw
        if isinstance(raw, str):
            low = raw.strip().lower()
            for m in enum_cls:
                if m.name.lower() == low or str(m.value).lower() == low:
                    return m
        raise _InvalidEnum(f"'{raw}' is not one of {[m.name for m in enum_cls]}")
    choices = list(getattr(col_type, "enums", []) or [])
    if isinstance(raw, str):
        low = raw.strip().lower()
        for c in choices:
            if c.lower() == low:
                return c
    raise _InvalidEnum(f"'{raw}' is not one of {choices or '[no choices defined]'}")


def _is_text_type(coltype):
    return isinstance(coltype, (String, Text))


def _looks_like_wildcard(s: str) -> bool:
    # treat '*' and '%' as wildcards
    return isinstance(s, str) and ("*" in s or "%" in s)


def _to_sql_like_pattern(s: str) -> str:
    if s is None:
        return None
    s = str(s)
    s = s.replace("*", "%")
    if "%" not in s:
        s = f"%{s}%"
    return s


def _parse_field_and_op(field: str):
    """
    Supports 'field__ilike' to force ILIKE.
    Returns (base_field, op) where op in {'eq', 'ilike'}
    """
    if "__" in field:
        base, op = field.rsplit("__", 1)
        if op.lower() == "ilike":
            return base, "ilike"
    return field, "eq"


def _apply_filters(pagination, entity, query):
    if not getattr(pagination, "filters", None):
        return query

    for raw_field, value in pagination.filters.items():
        if value is None or value in NULL_SENTINELS or value == [] or value == {}:
            value = None

        field, op_hint = _parse_field_and_op(raw_field)

        if not hasattr(entity, field):
            continue

        col = getattr(entity, field)
        coltype = getattr(col, "type", None)

        def coerce(v):
            if v is None:
                return None
            # Enums
            if isinstance(coltype, (SAEnum, PGEnum)):
                return _coerce_enum(coltype, v)
            # Text
            if _is_text_type(coltype):
                return str(v)
            # Numbers
            if isinstance(coltype, (Integer, BigInteger, SmallInteger)):
                return int(v)
            if isinstance(coltype, (Float, Numeric)):
                return float(v)
            # Booleans
            if isinstance(coltype, Boolean):
                if isinstance(v, bool): return v
                if isinstance(v, (int, float)): return bool(v)
                if isinstance(v, str):
                    vl = v.strip().lower()
                    if vl in {"true", "1", "yes", "y", "t"}: return True
                    if vl in {"false", "0", "no", "n", "f"}: return False
                return None
            # fallback
            return v

        try:
            # Decide operator: explicit __ilike OR automatic if wildcard on text
            def _use_ilike(v) -> bool:
                if op_hint == "ilike":
                    return True
                if _is_text_type(coltype) and isinstance(v, str) and _looks_like_wildcard(v):
                    return True
                return False

            if isinstance(value, (list, tuple, set)):
                vals = [v for v in value if v not in (None, "", "null", "None")]
                if not vals:
                    continue

                # if any value signals ilike, apply OR of ilike; else IN / EQs
                if any(_use_ilike(v) for v in vals) and _is_text_type(coltype):
                    patterns = [_to_sql_like_pattern(str(v)) for v in vals]
                    query = query.filter(or_(*[col.ilike(p) for p in patterns]))
                else:
                    coerced = [coerce(v) for v in vals]
                    if not coerced:
                        continue
                    query = query.filter(col.in_(coerced))
            else:
                if _use_ilike(value) and _is_text_type(coltype):
                    pattern = _to_sql_like_pattern(str(value))
                    query = query.filter(col.ilike(pattern))
                else:
                    v = coerce(value)
                    if v is None:
                        query = query.filter(col.is_(None))
                    else:
                        query = query.filter(col == v)

        except _InvalidEnum as e:
            # Surface validation error like before
            raise UnprocessableEntityException(str(e), loc=["query", "filters", raw_field]) from e

    return query


def apply_pagination(pagination: PaginateRequest, entity, session: Session, limit=True) -> Query:
    query = session.query(entity)
    query = _apply_filters(pagination, entity, query)
    query = _apply_order(pagination, entity, query)
    if limit:
        query = query.limit(pagination.limit).offset(pagination.offset)
    return query
