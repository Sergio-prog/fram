from enum import Enum
from typing import TypeVar

from fram.core.errors import InvalidOperation

EnumT = TypeVar("EnumT", bound=Enum)


def enum_value(enum_type: type[EnumT], value: str) -> EnumT:
    try:
        return enum_type(value)
    except ValueError as exc:
        allowed = ", ".join(item.value for item in enum_type)
        raise InvalidOperation(f"Invalid value '{value}'. Allowed: {allowed}.") from exc
