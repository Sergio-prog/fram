from fram.core.errors import InvalidOperation


def parse_timecode(value: str) -> float:
    parts = value.split(":")
    try:
        numbers = [float(part) for part in parts]
    except ValueError as exc:
        raise InvalidOperation(f"Invalid timecode: {value}") from exc

    if len(numbers) == 1:
        seconds = numbers[0]
    elif len(numbers) == 2:
        seconds = numbers[0] * 60 + numbers[1]
    elif len(numbers) == 3:
        seconds = numbers[0] * 3600 + numbers[1] * 60 + numbers[2]
    else:
        raise InvalidOperation("Timecode must be SS, MM:SS, or HH:MM:SS.")

    if seconds < 0:
        raise InvalidOperation("Timecode cannot be negative.")

    return seconds


def format_seconds(seconds: float) -> str:
    total = int(seconds)
    hours = total // 3600
    minutes = (total % 3600) // 60
    rest = total % 60
    if hours:
        return f"{hours:02d}:{minutes:02d}:{rest:02d}"
    return f"{minutes:02d}:{rest:02d}"

