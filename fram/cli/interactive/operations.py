from fram.core.errors import InvalidOperation
from fram.core.media import MediaType
from fram.core.operation_factory import (
    crop,
    cut,
    fps,
    image_compress,
    resize,
    strip_audio,
    video_compress,
)
from fram.core.operations import Operation, OperationName

IMAGE_ACTIONS = ["resize", "crop", "compress"]
VIDEO_ACTIONS = ["cut", "resize", "crop", "fps", "compress", "strip-audio"]

ACTION_LABELS = {
    "resize": "resize",
    "crop": "crop",
    "compress": "compress",
    "cut": "cut",
    "fps": "fps",
    "strip-audio": "strip-audio",
}

ACTION_HELP = {
    "resize": "size [mode], e.g. 128x128 fit",
    "crop": "size [anchor], e.g. 128x128 center",
    "compress": "image quality 1..100 or video CRF 0..51",
    "cut": "start end, or start duration value",
    "fps": "frames per second, e.g. 24",
    "strip-audio": "no params; press add/apply",
}

VALUE_PRESETS = {
    "resize": ["128x128 fit", "512x512 fit", "1024x1024 fit", "1280x720 exact"],
    "crop": ["128x128 center", "512x512 center", "1080x1080 center"],
    "compress": ["82", "70", "50", "23"],
    "cut": ["slider range", "5 10", "0 duration 10"],
    "fps": ["24", "30", "60"],
    "strip-audio": ["apply"],
}


def actions_for(media_type: MediaType | None) -> list[str]:
    if media_type == MediaType.VIDEO:
        return VIDEO_ACTIONS
    return IMAGE_ACTIONS


def value_presets_for(action: str, slider_value: str = "") -> list[str]:
    values = VALUE_PRESETS[action].copy()
    if action == "cut" and slider_value:
        values[0] = slider_value
    return values


def build_interactive_operation(
    action: str,
    media_type: MediaType,
    raw_value: str,
) -> Operation:
    value = raw_value.strip()
    if action == "resize":
        size, mode = _first_and_optional(value, "fit", "Resize needs size, e.g. 128x128.")
        return resize(size, mode)
    if action == "crop":
        size, anchor = _first_and_optional(value, "center", "Crop needs size, e.g. 128x128.")
        return crop(size, anchor)
    if action == "compress":
        number = _int_value(value, "Compression needs a number.")
        if media_type == MediaType.IMAGE:
            return image_compress(quality=number)
        return video_compress(crf=number)
    if action == "cut":
        return _build_cut(value)
    if action == "fps":
        return fps(_int_value(value, "FPS must be an integer."))
    if action == "strip-audio":
        return strip_audio()
    raise InvalidOperation(f"Unknown action: {action}")


def describe_operation(operation: Operation) -> str:
    params = operation.params
    match operation.name:
        case OperationName.RESIZE:
            return f"resize {params.size} mode={params.mode.value}"
        case OperationName.CROP:
            return f"crop {params.size} anchor={params.anchor.value}"
        case OperationName.COMPRESS:
            if hasattr(params, "quality"):
                return f"compress quality={params.quality}"
            return f"compress crf={params.crf} preset={params.preset}"
        case OperationName.CUT:
            if params.end_seconds is not None:
                return f"cut {params.start_seconds:g}s..{params.end_seconds:g}s"
            return f"cut {params.start_seconds:g}s duration={params.duration_seconds:g}s"
        case OperationName.FPS:
            return f"fps {params.fps}"
        case OperationName.STRIP_AUDIO:
            return "strip-audio"
        case _:
            return operation.name.value


def _build_cut(value: str) -> Operation:
    parts = _required(value, "Cut needs: start end, or start duration value.").split()
    if len(parts) == 2:
        return cut(start=parts[0], end=parts[1])
    if len(parts) == 3 and parts[1].lower() == "duration":
        return cut(start=parts[0], duration=parts[2])
    raise InvalidOperation("Cut format: start end, or start duration value.")


def _first_and_optional(value: str, default: str, message: str) -> tuple[str, str]:
    parts = _required(value, message).split()
    if len(parts) > 2:
        raise InvalidOperation(message)
    return parts[0], parts[1] if len(parts) == 2 else default


def _int_value(value: str, message: str) -> int:
    try:
        return int(_required(value, message))
    except ValueError as exc:
        raise InvalidOperation(message) from exc


def _required(value: str, message: str) -> str:
    if not value:
        raise InvalidOperation(message)
    return value
