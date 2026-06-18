from fram.core.media import MediaType

CHANNEL_HTML = '📣 <a href="https://t.me/there_is_no_meme">Channel</a>'
CHANNEL_MARKDOWN = "📣 [Channel](https://t.me/there_is_no_meme)"


def welcome() -> str:
    return (
        "👋 <b>Fram</b>\n\n"
        "Send me an image or video file. I can resize, crop, compress, and cut media.\n\n"
        "Best input: send media as a file/document when you want to preserve quality.\n\n"
        f"{CHANNEL_HTML}"
    )


def media_loaded(filename: str, media_type: MediaType) -> str:
    label = "image" if media_type == MediaType.IMAGE else "video"
    return (
        f"✅ Loaded <b>{filename}</b>\n"
        f"Type: <b>{label}</b>\n\n"
        "Choose what to do next."
    )


def action_prompt(action: str, media_type: MediaType) -> str:
    prompts = {
        "resize": "📐 Send target size, for example: <code>128x128</code>",
        "crop": "✂️ Send crop size, optionally with anchor: <code>128x128 center</code>",
        "compress": _compress_prompt(media_type),
        "cut": "🎞 Send range: <code>00:00:05 00:00:12</code> or <code>5 duration 10</code>",
        "fps": "🎚 Send FPS value, for example: <code>24</code>",
        "strip-audio": "🔇 Tap Apply to remove audio.",
        "strip-metadata": "🧹 Tap Apply to remove metadata.",
        "blur": "🌫 Send blur radius, for example: <code>2</code>",
        "grayscale": "⚫ Tap Apply to convert to grayscale.",
        "convert": "🔁 Send output format, for example: <code>webp</code> or <code>mp4</code>",
        "rotate": "↻ Send clockwise degrees, for example: <code>90</code>",
        "flip": "↔️ Send <code>horizontal</code>, <code>vertical</code>, or <code>both</code>",
        "extract-audio": "🎧 Tap Apply to extract audio.",
        "extract-frame": "🖼 Send timestamp, for example: <code>00:00:05</code>",
        "gif": "GIF: send FPS and optional width, for example: <code>12 480</code>",
        "speed": "⏩ Send speed factor, for example: <code>2</code> or <code>0.5</code>",
        "reverse": "↩️ Tap Apply to reverse video.",
        "mute-audio": "🔈 Tap Apply to mute audio.",
        "thumbnail": "Send thumbnail timestamp, for example: <code>00:00:05</code>",
        "contact-sheet": (
            "Send columns, rows, and optional width, for example: <code>3 3 320</code>"
        ),
        "extract-subtitles": "Send subtitle stream index, for example: <code>0</code>",
        "sharpen": "Send sharpen factor, for example: <code>2</code>",
        "watermark": (
            "Send watermark text, or text opacity position size, "
            "for example: <code>FRAM 0.75 bottom-right 32</code>"
        ),
        "upscale": "Send upscale factor, for example: <code>2</code>",
        "auto-orient": "Tap Apply to auto-orient the image.",
        "background": (
            "Send background color, for example: <code>white</code> or <code>#ffffff</code>"
        ),
    }
    return prompts[action]


def operation_added(count: int) -> str:
    noun = "operation" if count == 1 else "operations"
    return f"Added. Pipeline has <b>{count}</b> {noun}."


def processing() -> str:
    return "⚙️ Processing media..."


def done() -> str:
    return f"✅ Done.\n\n{CHANNEL_HTML}"


def cancelled() -> str:
    return "Cancelled. Send another image or video when ready."


def invalid_input(error: str) -> str:
    return f"⚠️ {error}\n\nTry again or tap Cancel."


def unsupported() -> str:
    return "⚠️ I could not use this media type yet. Try jpg, png, webp, mp4, mov, mkv, or webm."


def _compress_prompt(media_type: MediaType) -> str:
    if media_type == MediaType.IMAGE:
        return (
            "🗜 Send image quality from <code>1</code> to <code>100</code>. "
            "Good default: <code>82</code>"
        )
    return "🗜 Send CRF from <code>0</code> to <code>51</code>. Good default: <code>23</code>"
