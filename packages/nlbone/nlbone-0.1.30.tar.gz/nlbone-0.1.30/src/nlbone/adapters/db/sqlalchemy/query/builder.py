from __future__ import annotations
from sqlalchemy.orm import Session, Query

from nlbone.adapters.db.sqlalchemy.query.filters import apply_filters_to_query
from nlbone.adapters.db.sqlalchemy.query.ordering import apply_order_to_query


def apply_pagination(pagination, entity, session: Session, limit: bool = True) -> Query:
    q: Query = session.query(entity)
    q = apply_filters_to_query(pagination, entity, q)
    from nlbone.adapters.db.sqlalchemy.query.ordering import apply_order_to_query
    q = apply_order_to_query(pagination, entity, q)
    if limit:
        q = q.limit(pagination.limit).offset(pagination.offset)
    return q

def apply_filters(pagination, entity, query: Query) -> Query:
    return apply_filters_to_query(pagination, entity, query)

def apply_order(pagination, entity, query: Query) -> Query:
    return apply_order_to_query(pagination, entity, query)
