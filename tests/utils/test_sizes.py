import pytest

from fram.core.errors import InvalidOperation
from fram.utils.sizes import Size, parse_size


def test_parse_size() -> None:
    assert parse_size("128x256") == Size(width=128, height=256)
    assert parse_size(" 128 X 256 ") == Size(width=128, height=256)


@pytest.mark.parametrize("value", ["128", "x128", "128x0", "-1x128", "axb"])
def test_parse_size_rejects_invalid_values(value: str) -> None:
    with pytest.raises(InvalidOperation):
        parse_size(value)

