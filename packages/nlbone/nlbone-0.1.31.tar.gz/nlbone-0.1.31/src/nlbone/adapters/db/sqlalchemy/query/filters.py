from __future__ import annotations
from sqlalchemy import or_
from sqlalchemy.orm import Query

try:
    from sqlalchemy.dialects.postgresql import ENUM as PGEnum  # اختیاری
except Exception:
    PGEnum = type("PGEnum", (), {})  # fallback dummy

from nlbone.interfaces.api.exceptions import UnprocessableEntityException
from nlbone.interfaces.api.pagination import PaginateRequest
from .coercion import coerce_value_for_column, to_like_pattern, is_text_type, looks_like_wildcard
from .types import NULL_SENTINELS, InvalidEnum, parse_field_and_op

def apply_filters_to_query(pagination: PaginateRequest, entity, query: Query) -> Query:
    if not getattr(pagination, "filters", None):
        return query

    for raw_field, value in pagination.filters.items():
        if value is None or value in NULL_SENTINELS or value == [] or value == {}:
            value = None

        field, op_hint = parse_field_and_op(raw_field)
        if not hasattr(entity, field):
            continue

        col = getattr(entity, field)
        coltype = getattr(col, "type", None)

        def _use_ilike(v) -> bool:
            if op_hint == "ilike":
                return True
            return is_text_type(coltype) and isinstance(v, str) and looks_like_wildcard(v)

        try:
            if isinstance(value, (list, tuple, set)):
                vals = [v for v in value if v not in (None, "", "null", "None")]
                if not vals:
                    continue
                if any(_use_ilike(v) for v in vals) and is_text_type(coltype):
                    patterns = [to_like_pattern(str(v)) for v in vals]
                    query = query.filter(or_(*[col.ilike(p) for p in patterns]))
                else:
                    coerced = [coerce_value_for_column(coltype, v) for v in vals]
                    if not coerced:
                        continue
                    query = query.filter(col.in_(coerced))
            else:
                if _use_ilike(value) and is_text_type(coltype):
                    query = query.filter(col.ilike(to_like_pattern(str(value))))
                else:
                    v = coerce_value_for_column(coltype, value)
                    query = query.filter(col.is_(None) if v is None else (col == v))
        except InvalidEnum as e:
            raise UnprocessableEntityException(str(e), loc=["query", "filters", raw_field]) from e

    return query
