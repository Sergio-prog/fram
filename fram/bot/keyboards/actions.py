from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

ACTION_LABELS = {
    "resize": "📐 Resize",
    "crop": "✂️ Crop",
    "compress": "🗜 Compress",
    "cut": "🎞 Cut",
    "fps": "🎚 FPS",
    "strip-audio": "🔇 Strip audio",
    "strip-metadata": "🧹 Strip metadata",
    "blur": "🌫 Blur",
    "grayscale": "⚫ Grayscale",
    "convert": "🔁 Convert",
    "rotate": "↻ Rotate",
    "flip": "↔️ Flip",
    "extract-audio": "🎧 Audio",
    "extract-frame": "🖼 Frame",
    "gif": "GIF",
    "speed": "⏩ Speed",
    "reverse": "↩️ Reverse",
}


def media_actions_keyboard(is_video: bool) -> InlineKeyboardMarkup:
    actions = [
        "resize",
        "crop",
        "compress",
        "convert",
        "rotate",
        "flip",
        "strip-metadata",
        "blur",
        "grayscale",
    ]
    if is_video:
        actions = [
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
        ]
    buttons = [
        [InlineKeyboardButton(text=ACTION_LABELS[action], callback_data=f"action:{action}")]
        for action in actions
    ]
    buttons.append([InlineKeyboardButton(text="📣 Channel", url="https://t.me/there_is_no_meme")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Apply", callback_data="confirm:apply")],
            [InlineKeyboardButton(text="↩️ Cancel", callback_data="confirm:cancel")],
        ]
    )


def cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="↩️ Cancel", callback_data="confirm:cancel")]]
    )
