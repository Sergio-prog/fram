from fram.core.errors import InvalidOperation
from fram.core.media import MediaType
from fram.core.operation_factory import (
    crop,
    cut,
    extract_frame,
    fps,
    image_compress,
    resize,
    strip_audio,
    video_compress,
)
from fram.core.operations import Operation

NO_PARAM_ACTIONS = {"strip-audio"}


def build_operation(action: str, media_type: MediaType, raw_value: str | None = None) -> Operation:
    value = (raw_value or "").strip()

    if action == "resize":
        return resize(_required(value, "Send a size like 128x128."))
    if action == "crop":
        return _build_crop(value)
    if action == "compress":
        return _build_compress(media_type, value)
    if action == "cut":
        return _build_cut(value)
    if action == "fps":
        return fps(_int_value(value, "FPS must be an integer."))
    if action == "strip-audio":
        return strip_audio()
    if action == "extract-frame":
        return extract_frame(_required(value, "Send a timestamp like 00:00:05."))

    raise InvalidOperation(f"Unknown action: {action}")


def _build_crop(value: str) -> Operation:
    parts = _required(value, "Send a crop size like 128x128.").split()
    if len(parts) > 2:
        raise InvalidOperation("Crop format: 128x128 or 128x128 center.")
    return crop(parts[0], parts[1] if len(parts) == 2 else "center")


def _build_compress(media_type: MediaType, value: str) -> Operation:
    number = _int_value(value, "Compression value must be an integer.")
    if media_type == MediaType.IMAGE:
        return image_compress(quality=number)
    return video_compress(crf=number)


def _build_cut(value: str) -> Operation:
    parts = _required(value, "Send a range like 00:00:05 00:00:12.").split()
    if len(parts) == 2:
        return cut(start=parts[0], end=parts[1])
    if len(parts) == 3 and parts[1].lower() == "duration":
        return cut(start=parts[0], duration=parts[2])
    raise InvalidOperation("Cut format: start end, or start duration seconds.")


def _required(value: str, message: str) -> str:
    if not value:
        raise InvalidOperation(message)
    return value


def _int_value(value: str, message: str) -> int:
    try:
        return int(_required(value, message))
    except ValueError as exc:
        raise InvalidOperation(message) from exc
