from sqlalchemy.sql.sqltypes import (
    String, Text, Integer, BigInteger, SmallInteger, Numeric, Float, Boolean, Enum as SAEnum
)
try:
    from sqlalchemy.dialects.postgresql import ENUM as PGEnum
except Exception:
    PGEnum = type("PGEnum", (), {})

from .types import InvalidEnum

def is_text_type(coltype) -> bool:
    return isinstance(coltype, (String, Text))

def looks_like_wildcard(s: str) -> bool:
    return isinstance(s, str) and ("*" in s or "%" in s)

def to_like_pattern(s: str) -> str:
    s = (s or "")
    s = s.replace("*", "%")
    return s if "%" in s else f"%{s}%"

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
        raise InvalidEnum(f"'{raw}' is not one of {[m.name for m in enum_cls]}")
    choices = list(getattr(col_type, "enums", []) or [])
    if isinstance(raw, str):
        low = raw.strip().lower()
        for c in choices:
            if c.lower() == low:
                return c
    raise InvalidEnum(f"'{raw}' is not one of {choices or '[no choices defined]'}")

def coerce_value_for_column(coltype, v):
    if v is None:
        return None
    if isinstance(coltype, (SAEnum, PGEnum)):
        return _coerce_enum(coltype, v)
    if is_text_type(coltype):
        return str(v)
    if isinstance(coltype, (Integer, BigInteger, SmallInteger)):
        return int(v)
    if isinstance(coltype, (Float, Numeric)):
        return float(v)
    if isinstance(coltype, Boolean):
        if isinstance(v, bool):
            return v
        if isinstance(v, (int, float)):
            return bool(v)
        if isinstance(v, str):
            vl = v.strip().lower()
            if vl in {"true", "1", "yes", "y", "t"}: return True
            if vl in {"false", "0", "no", "n", "f"}: return False
        return None
    return v
