from __future__ import annotations
from sqlalchemy.orm import Session, Query
from .filters import apply_filters_to_query
from .ordering import apply_order_to_query

def apply_pagination(pagination, entity, session: Session, limit: bool = True) -> Query:
    q: Query = session.query(entity)
    q = apply_filters_to_query(pagination, entity, q)
    q = apply_order_to_query(pagination, entity, q)
    if limit:
        q = q.limit(pagination.limit).offset(pagination.offset)
    return q

# اگر خواستی به صورت جدا گونه هم اکسپورت کن:
def apply_filters(pagination, entity, query: Query) -> Query:
    return apply_filters_to_query(pagination, entity, query)

def apply_order(pagination, entity, query: Query) -> Query:
    return apply_order_to_query(pagination, entity, query)
