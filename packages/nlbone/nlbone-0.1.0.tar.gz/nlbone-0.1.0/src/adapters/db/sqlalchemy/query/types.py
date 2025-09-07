NULL_SENTINELS = {"None", "null", ""}

class InvalidEnum(Exception):
    pass

def parse_field_and_op(field: str) -> tuple[str, str]:
    if "__" in field:
        base, op = field.rsplit("__", 1)
        if op.lower() == "ilike":
            return base, "ilike"
    return field, "eq"
