from fram.core.errors import InvalidOperation
from fram.core.media import MediaType
from fram.core.operation_factory import (
    adjust,
    auto_orient,
    background,
    blur,
    contact_sheet,
    convert,
    crop,
    cut,
    extract_audio,
    extract_frame,
    extract_subtitles,
    flip,
    fps,
    gif,
    grayscale,
    image_compress,
    mute_audio,
    resize,
    reverse,
    rotate,
    sharpen,
    speed,
    strip_audio,
    strip_metadata,
    thumbnail,
    upscale,
    video_compress,
    watermark,
)
from fram.core.operations import Operation, OperationName

IMAGE_ACTIONS = [
    "resize",
    "crop",
    "compress",
    "convert",
    "rotate",
    "flip",
    "strip-metadata",
    "blur",
    "grayscale",
    "adjust",
    "sharpen",
    "watermark",
    "upscale",
    "auto-orient",
    "background",
]
VIDEO_ACTIONS = [
    "cut",
    "resize",
    "crop",
    "fps",
    "compress",
    "convert",
    "strip-audio",
    "strip-metadata",
    "blur",
    "grayscale",
    "extract-audio",
    "extract-frame",
    "gif",
    "speed",
    "reverse",
    "mute-audio",
    "thumbnail",
    "contact-sheet",
    "extract-subtitles",
]

ACTION_LABELS = {
    "resize": "📐 resize",
    "crop": "✂️ crop",
    "compress": "🗜 compress",
    "cut": "🎞 cut",
    "fps": "🎚 fps",
    "strip-audio": "🔇 strip-audio",
    "strip-metadata": "🧹 strip-metadata",
    "blur": "🌫 blur",
    "grayscale": "⚫ grayscale",
    "adjust": "☀ adjust",
    "sharpen": "△ sharpen",
    "watermark": "WM watermark",
    "upscale": "⤢ upscale",
    "auto-orient": "↟ auto-orient",
    "background": "▣ background",
    "convert": "🔁 convert",
    "rotate": "↻ rotate",
    "flip": "↔ flip",
    "extract-audio": "🎧 extract-audio",
    "extract-frame": "🖼 extract-frame",
    "gif": "🎞 GIF",
    "speed": "⏩ speed",
    "reverse": "↩ reverse",
    "mute-audio": "🔈 mute-audio",
    "thumbnail": "▣ thumbnail",
    "contact-sheet": "▦ contact-sheet",
    "extract-subtitles": "CC extract-subtitles",
}

ACTION_HELP = {
    "resize": "size [mode], e.g. 128x128 fit",
    "crop": "size [anchor], e.g. 128x128 center",
    "compress": "image quality 1..100 or video CRF 0..51",
    "cut": "start end, or start duration value",
    "fps": "frames per second, e.g. 24",
    "strip-audio": "no params; press add/apply",
    "strip-metadata": "no params; press add/apply",
    "blur": "radius, e.g. 2",
    "grayscale": "no params; press add/apply",
    "adjust": "brightness [contrast], e.g. 1.1 1.2",
    "sharpen": "factor, e.g. 2",
    "watermark": "text [opacity position size]",
    "upscale": "factor, e.g. 2",
    "auto-orient": "no params; press add/apply",
    "background": "color, e.g. white or #ffffff",
    "convert": "format, e.g. webp, png, jpg, gif, mp4",
    "rotate": "clockwise degrees, e.g. 90",
    "flip": "horizontal, vertical, or both",
    "extract-audio": "no params; press add/apply",
    "extract-frame": "timestamp, e.g. 00:00:05",
    "gif": "fps [width], e.g. 12 480",
    "speed": "factor, e.g. 2 or 0.5",
    "reverse": "no params, or no-audio",
    "mute-audio": "no params; press add/apply",
    "thumbnail": "timestamp, e.g. 00:00:05",
    "contact-sheet": "columns rows [width], e.g. 3 3 320",
    "extract-subtitles": "stream index, e.g. 0",
}

VALUE_PRESETS = {
    "resize": ["128x128 fit", "512x512 fit", "1024x1024 fit", "1280x720 exact"],
    "crop": ["128x128 center", "512x512 center", "1080x1080 center"],
    "compress": ["82", "70", "50", "23"],
    "cut": ["slider range", "5 10", "0 duration 10"],
    "fps": ["24", "30", "60"],
    "strip-audio": ["apply"],
    "strip-metadata": ["apply"],
    "blur": ["2", "5", "10"],
    "grayscale": ["apply"],
    "adjust": ["1.1 1.1", "0.9 1.2", "1.2 1"],
    "sharpen": ["2", "3", "0"],
    "watermark": ["FRAM 0.75 bottom-right 32"],
    "upscale": ["2", "1.5", "3"],
    "auto-orient": ["apply"],
    "background": ["white", "#ffffff", "black"],
    "convert": ["webp", "png", "jpg", "mp4", "gif"],
    "rotate": ["90", "180", "270"],
    "flip": ["horizontal", "vertical", "both"],
    "extract-audio": ["apply"],
    "extract-frame": ["00:00:05", "5"],
    "gif": ["12", "12 480", "15 720"],
    "speed": ["2", "0.5", "1.25"],
    "reverse": ["apply", "no-audio"],
    "mute-audio": ["apply"],
    "thumbnail": ["00:00:05", "5"],
    "contact-sheet": ["3 3 320", "4 4 240"],
    "extract-subtitles": ["0"],
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
    if action == "strip-metadata":
        return strip_metadata()
    if action == "blur":
        return blur(_float_value(value or "2", "Blur radius must be a number."))
    if action == "grayscale":
        return grayscale()
    if action == "adjust":
        return _build_adjust(value)
    if action == "sharpen":
        return sharpen(_float_value(value or "2", "Sharpen factor must be a number."))
    if action == "watermark":
        return _build_watermark(value)
    if action == "upscale":
        return upscale(_float_value(value or "2", "Upscale factor must be a number."))
    if action == "auto-orient":
        return auto_orient()
    if action == "background":
        return background(_required(value, "Background needs a color."))
    if action == "convert":
        return convert(_required(value, "Convert needs a format, e.g. webp."))
    if action == "rotate":
        return rotate(_int_value(value, "Degrees must be an integer."))
    if action == "flip":
        return _build_flip(value)
    if action == "extract-audio":
        return extract_audio()
    if action == "extract-frame":
        return extract_frame(_required(value, "Extract frame needs a timestamp."))
    if action == "gif":
        return _build_gif(value)
    if action == "speed":
        return speed(_float_value(value, "Speed factor must be a number."))
    if action == "reverse":
        return reverse(include_audio=value.lower() != "no-audio")
    if action == "mute-audio":
        return mute_audio()
    if action == "thumbnail":
        return thumbnail(value or "0")
    if action == "contact-sheet":
        return _build_contact_sheet(value)
    if action == "extract-subtitles":
        return extract_subtitles(_int_value(value or "0", "Subtitle stream index must be integer."))
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
        case OperationName.STRIP_METADATA:
            return "strip-metadata"
        case OperationName.BLUR:
            return f"blur radius={params.radius:g}"
        case OperationName.GRAYSCALE:
            return "grayscale"
        case OperationName.ADJUST:
            return f"adjust brightness={params.brightness:g} contrast={params.contrast:g}"
        case OperationName.SHARPEN:
            return f"sharpen factor={params.factor:g}"
        case OperationName.WATERMARK:
            return (
                f"watermark {params.text!r} opacity={params.opacity:g} "
                f"position={params.position.value} size={params.size}"
            )
        case OperationName.UPSCALE:
            return f"upscale {params.factor:g}x"
        case OperationName.AUTO_ORIENT:
            return "auto-orient"
        case OperationName.BACKGROUND:
            return f"background {params.color}"
        case OperationName.CONVERT:
            return f"convert {params.format}"
        case OperationName.ROTATE:
            return f"rotate {params.degrees}"
        case OperationName.FLIP:
            directions = []
            if params.horizontal:
                directions.append("horizontal")
            if params.vertical:
                directions.append("vertical")
            return f"flip {'+'.join(directions)}"
        case OperationName.EXTRACT_AUDIO:
            return "extract-audio"
        case OperationName.EXTRACT_FRAME:
            return f"extract-frame at={params.at_seconds:g}s"
        case OperationName.GIF:
            width = f" width={params.width}" if params.width is not None else ""
            return f"gif fps={params.fps}{width}"
        case OperationName.SPEED:
            return f"speed {params.factor:g}x"
        case OperationName.REVERSE:
            return "reverse" if params.include_audio else "reverse no-audio"
        case OperationName.MUTE_AUDIO:
            return "mute-audio"
        case OperationName.THUMBNAIL:
            return f"thumbnail at={params.at_seconds:g}s"
        case OperationName.CONTACT_SHEET:
            return (
                f"contact-sheet {params.columns}x{params.rows} "
                f"width={params.width}"
            )
        case OperationName.EXTRACT_SUBTITLES:
            return f"extract-subtitles stream={params.stream_index}"
        case _:
            return operation.name.value


def _build_cut(value: str) -> Operation:
    parts = _required(value, "Cut needs: start end, or start duration value.").split()
    if len(parts) == 2:
        return cut(start=parts[0], end=parts[1])
    if len(parts) == 3 and parts[1].lower() == "duration":
        return cut(start=parts[0], duration=parts[2])
    raise InvalidOperation("Cut format: start end, or start duration value.")


def _build_flip(value: str) -> Operation:
    direction = _required(value, "Flip needs: horizontal, vertical, or both.").lower()
    if direction in {"horizontal", "h"}:
        return flip(horizontal=True)
    if direction in {"vertical", "v"}:
        return flip(vertical=True)
    if direction in {"both", "all"}:
        return flip(horizontal=True, vertical=True)
    raise InvalidOperation("Flip format: horizontal, vertical, or both.")


def _build_gif(value: str) -> Operation:
    parts = (value or "12").split()
    if len(parts) > 2:
        raise InvalidOperation("GIF format: fps, or fps width.")
    fps_value = _int_value(parts[0], "GIF FPS must be an integer.")
    width = _int_value(parts[1], "GIF width must be an integer.") if len(parts) == 2 else None
    return gif(fps_value, width)


def _build_adjust(value: str) -> Operation:
    parts = (value or "1 1").split()
    if len(parts) > 2:
        raise InvalidOperation("Adjust format: brightness, or brightness contrast.")
    brightness = _float_value(parts[0], "Brightness must be a number.")
    contrast = _float_value(parts[1], "Contrast must be a number.") if len(parts) == 2 else 1.0
    return adjust(brightness, contrast)


def _build_watermark(value: str) -> Operation:
    parts = _required(value, "Watermark needs text.").split()
    if len(parts) == 1:
        return watermark(parts[0])
    if len(parts) == 4:
        return watermark(
            parts[0],
            opacity=_float_value(parts[1], "Watermark opacity must be a number."),
            position=parts[2],
            size=_int_value(parts[3], "Watermark size must be an integer."),
        )
    raise InvalidOperation("Watermark format: text, or text opacity position size.")


def _build_contact_sheet(value: str) -> Operation:
    parts = (value or "3 3 320").split()
    if len(parts) not in {2, 3}:
        raise InvalidOperation("Contact sheet format: columns rows [width].")
    columns = _int_value(parts[0], "Contact sheet columns must be an integer.")
    rows = _int_value(parts[1], "Contact sheet rows must be an integer.")
    width = (
        _int_value(parts[2], "Contact sheet width must be an integer.")
        if len(parts) == 3
        else 320
    )
    return contact_sheet(columns, rows, width)


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


def _float_value(value: str, message: str) -> float:
    try:
        return float(_required(value, message))
    except ValueError as exc:
        raise InvalidOperation(message) from exc


def _required(value: str, message: str) -> str:
    if not value:
        raise InvalidOperation(message)
    return value
