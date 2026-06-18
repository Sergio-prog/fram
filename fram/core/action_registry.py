from dataclasses import dataclass

from fram.core.media import MediaType


@dataclass(frozen=True)
class ActionSpec:
    name: str
    media_types: tuple[MediaType, ...]
    cli_label: str
    bot_label: str
    help_text: str
    presets: tuple[str, ...]
    no_value: bool = False


ACTION_SPECS: tuple[ActionSpec, ...] = (
    ActionSpec(
        "resize",
        (MediaType.IMAGE, MediaType.VIDEO),
        "📐 resize",
        "📐 Resize",
        "size [mode], e.g. 128x128 fit",
        ("128x128 fit", "512x512 fit", "1024x1024 fit", "1280x720 exact"),
    ),
    ActionSpec(
        "crop",
        (MediaType.IMAGE, MediaType.VIDEO),
        "✂️ crop",
        "✂️ Crop",
        "size [anchor], e.g. 128x128 center",
        ("128x128 center", "512x512 center", "1080x1080 center"),
    ),
    ActionSpec(
        "compress",
        (MediaType.IMAGE, MediaType.VIDEO),
        "🗜 compress",
        "🗜 Compress",
        "image quality 1..100 or video CRF 0..51",
        ("82", "70", "50", "23"),
    ),
    ActionSpec(
        "convert",
        (MediaType.IMAGE, MediaType.VIDEO),
        "🔁 convert",
        "🔁 Convert",
        "format, e.g. webp, png, jpg, gif, mp4",
        ("webp", "png", "jpg", "mp4", "gif"),
    ),
    ActionSpec(
        "rotate",
        (MediaType.IMAGE, MediaType.VIDEO),
        "↻ rotate",
        "↻ Rotate",
        "clockwise degrees, e.g. 90",
        ("90", "180", "270"),
    ),
    ActionSpec(
        "flip",
        (MediaType.IMAGE, MediaType.VIDEO),
        "↔ flip",
        "↔️ Flip",
        "horizontal, vertical, or both",
        ("horizontal", "vertical", "both"),
    ),
    ActionSpec(
        "strip-metadata",
        (MediaType.IMAGE, MediaType.VIDEO),
        "🧹 strip-metadata",
        "🧹 Strip metadata",
        "no params; press add/apply",
        ("apply",),
        no_value=True,
    ),
    ActionSpec(
        "blur",
        (MediaType.IMAGE, MediaType.VIDEO),
        "🌫 blur",
        "🌫 Blur",
        "radius, e.g. 2",
        ("2", "5", "10"),
    ),
    ActionSpec(
        "grayscale",
        (MediaType.IMAGE, MediaType.VIDEO),
        "⚫ grayscale",
        "⚫ Grayscale",
        "no params; press add/apply",
        ("apply",),
        no_value=True,
    ),
    ActionSpec(
        "adjust",
        (MediaType.IMAGE,),
        "☀ adjust",
        "☀ Adjust",
        "brightness [contrast], e.g. 1.1 1.2",
        ("1.1 1.1", "0.9 1.2", "1.2 1"),
    ),
    ActionSpec(
        "sharpen",
        (MediaType.IMAGE,),
        "△ sharpen",
        "Sharpen",
        "factor, e.g. 2",
        ("2", "3", "0"),
    ),
    ActionSpec(
        "watermark",
        (MediaType.IMAGE,),
        "WM watermark",
        "Watermark",
        "text [opacity position size]",
        ("FRAM 0.75 bottom-right 32",),
    ),
    ActionSpec(
        "upscale",
        (MediaType.IMAGE,),
        "⤢ upscale",
        "Upscale",
        "factor, e.g. 2",
        ("2", "1.5", "3"),
    ),
    ActionSpec(
        "auto-orient",
        (MediaType.IMAGE,),
        "↟ auto-orient",
        "Auto-orient",
        "no params; press add/apply",
        ("apply",),
        no_value=True,
    ),
    ActionSpec(
        "background",
        (MediaType.IMAGE,),
        "▣ background",
        "Background",
        "color, e.g. white or #ffffff",
        ("white", "#ffffff", "black"),
    ),
    ActionSpec(
        "cut",
        (MediaType.VIDEO,),
        "🎞 cut",
        "🎞 Cut",
        "start end, or start duration value",
        ("slider range", "5 10", "0 duration 10"),
    ),
    ActionSpec(
        "fps",
        (MediaType.VIDEO,),
        "🎚 fps",
        "🎚 FPS",
        "frames per second, e.g. 24",
        ("24", "30", "60"),
    ),
    ActionSpec(
        "strip-audio",
        (MediaType.VIDEO,),
        "🔇 strip-audio",
        "🔇 Strip audio",
        "no params; press add/apply",
        ("apply",),
        no_value=True,
    ),
    ActionSpec(
        "extract-audio",
        (MediaType.VIDEO,),
        "🎧 extract-audio",
        "🎧 Audio",
        "no params; press add/apply",
        ("apply",),
        no_value=True,
    ),
    ActionSpec(
        "extract-frame",
        (MediaType.VIDEO,),
        "🖼 extract-frame",
        "🖼 Frame",
        "timestamp, e.g. 00:00:05",
        ("00:00:05", "5"),
    ),
    ActionSpec(
        "gif",
        (MediaType.VIDEO,),
        "🎞 GIF",
        "GIF",
        "fps [width], e.g. 12 480",
        ("12", "12 480", "15 720"),
    ),
    ActionSpec(
        "speed",
        (MediaType.VIDEO,),
        "⏩ speed",
        "⏩ Speed",
        "factor, e.g. 2 or 0.5",
        ("2", "0.5", "1.25"),
    ),
    ActionSpec(
        "reverse",
        (MediaType.VIDEO,),
        "↩ reverse",
        "↩️ Reverse",
        "no params, or no-audio",
        ("apply", "no-audio"),
        no_value=True,
    ),
    ActionSpec(
        "mute-audio",
        (MediaType.VIDEO,),
        "🔈 mute-audio",
        "🔈 Mute audio",
        "no params; press add/apply",
        ("apply",),
        no_value=True,
    ),
    ActionSpec(
        "thumbnail",
        (MediaType.VIDEO,),
        "▣ thumbnail",
        "Thumbnail",
        "timestamp, e.g. 00:00:05",
        ("00:00:05", "5"),
    ),
    ActionSpec(
        "contact-sheet",
        (MediaType.VIDEO,),
        "▦ contact-sheet",
        "Contact sheet",
        "columns rows [width], e.g. 3 3 320",
        ("3 3 320", "4 4 240"),
    ),
    ActionSpec(
        "extract-subtitles",
        (MediaType.VIDEO,),
        "CC extract-subtitles",
        "Subtitles",
        "stream index, e.g. 0",
        ("0",),
    ),
)

ACTION_BY_NAME = {spec.name: spec for spec in ACTION_SPECS}


def actions_for_media(media_type: MediaType) -> list[str]:
    return [spec.name for spec in ACTION_SPECS if media_type in spec.media_types]


def no_value_actions() -> set[str]:
    return {spec.name for spec in ACTION_SPECS if spec.no_value}
