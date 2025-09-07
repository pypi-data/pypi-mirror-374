from sqlalchemy import asc, desc
from sqlalchemy.orm import Query

def apply_order_to_query(pagination, entity, query: Query) -> Query:
    if not pagination.sort:
        return query
    clauses = []
    for s in pagination.sort:
        field = s["field"]
        order = s["order"]
        if hasattr(entity, field):
            col = getattr(entity, field)
            clauses.append(asc(col) if order == "asc" else desc(col))
    return query.order_by(*clauses) if clauses else query
