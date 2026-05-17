from dataclasses import dataclass

from fram.core.errors import InvalidOperation


@dataclass(frozen=True)
class Size:
    width: int
    height: int

    def as_tuple(self) -> tuple[int, int]:
        return self.width, self.height

    def __str__(self) -> str:
        return f"{self.width}x{self.height}"


def parse_size(value: str) -> Size:
    normalized = value.lower().replace(" ", "")
    parts = normalized.split("x")
    if len(parts) != 2:
        raise InvalidOperation("Size must use WIDTHxHEIGHT format, for example 128x128.")

    try:
        width = int(parts[0])
        height = int(parts[1])
    except ValueError as exc:
        raise InvalidOperation("Size width and height must be integers.") from exc

    if width <= 0 or height <= 0:
        raise InvalidOperation("Size width and height must be greater than zero.")

    return Size(width=width, height=height)

