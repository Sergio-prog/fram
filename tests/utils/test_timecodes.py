import pytest

from fram.core.errors import InvalidOperation
from fram.utils.timecodes import format_seconds, parse_timecode


@pytest.mark.parametrize(
    ("value", "seconds"),
    [
        ("5", 5),
        ("01:05", 65),
        ("01:02:03", 3723),
    ],
)
def test_parse_timecode(value: str, seconds: float) -> None:
    assert parse_timecode(value) == seconds


@pytest.mark.parametrize("value", ["", "1:2:3:4", "-1", "abc"])
def test_parse_timecode_rejects_invalid_values(value: str) -> None:
    with pytest.raises(InvalidOperation):
        parse_timecode(value)


@pytest.mark.parametrize(
    ("seconds", "formatted"),
    [
        (65, "01:05"),
        (3723, "01:02:03"),
    ],
)
def test_format_seconds(seconds: float, formatted: str) -> None:
    assert format_seconds(seconds) == formatted

