from fram.core.errors import InvalidOperation
from fram.core.media import MediaType
from fram.core.operation_factory import (
    blur,
    convert,
    crop,
    cut,
    extract_audio,
    extract_frame,
    flip,
    fps,
    gif,
    grayscale,
    image_compress,
    resize,
    reverse,
    rotate,
    speed,
    strip_audio,
    strip_metadata,
    video_compress,
)
from fram.core.operations import Operation

NO_PARAM_ACTIONS = {"strip-audio", "strip-metadata", "grayscale", "extract-audio", "reverse"}


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
    if action == "strip-metadata":
        return strip_metadata()
    if action == "blur":
        return blur(_float_value(value or "2", "Blur radius must be a number."))
    if action == "grayscale":
        return grayscale()
    if action == "convert":
        return convert(_required(value, "Send a format like webp, png, jpg, gif, or mp4."))
    if action == "rotate":
        return rotate(_int_value(value, "Degrees must be an integer."))
    if action == "flip":
        return _build_flip(value)
    if action == "extract-audio":
        return extract_audio()
    if action == "extract-frame":
        return extract_frame(_required(value, "Send a timestamp like 00:00:05."))
    if action == "gif":
        return _build_gif(value)
    if action == "speed":
        return speed(_float_value(value, "Speed factor must be a number."))
    if action == "reverse":
        return reverse()

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


def _build_flip(value: str) -> Operation:
    direction = _required(value, "Send flip direction: horizontal, vertical, or both.").lower()
    if direction in {"horizontal", "h"}:
        return flip(horizontal=True)
    if direction in {"vertical", "v"}:
        return flip(vertical=True)
    if direction in {"both", "all"}:
        return flip(horizontal=True, vertical=True)
    raise InvalidOperation("Flip direction must be horizontal, vertical, or both.")


def _build_gif(value: str) -> Operation:
    parts = (value or "12").split()
    if len(parts) > 2:
        raise InvalidOperation("GIF format: fps, or fps width.")
    fps_value = _int_value(parts[0], "GIF FPS must be an integer.")
    width = _int_value(parts[1], "GIF width must be an integer.") if len(parts) == 2 else None
    return gif(fps_value, width)


def _required(value: str, message: str) -> str:
    if not value:
        raise InvalidOperation(message)
    return value


def _int_value(value: str, message: str) -> int:
    try:
        return int(_required(value, message))
    except ValueError as exc:
        raise InvalidOperation(message) from exc


def _float_value(value: str, message: str) -> float:
    try:
        return float(_required(value, message))
    except ValueError as exc:
        raise InvalidOperation(message) from exc
