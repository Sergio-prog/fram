from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

ACTION_LABELS = {
    "resize": "📐 Resize",
    "crop": "✂️ Crop",
    "compress": "🗜 Compress",
    "cut": "🎞 Cut",
    "fps": "🎚 FPS",
    "strip-audio": "🔇 Strip audio",
    "extract-frame": "🖼 Frame",
}


def media_actions_keyboard(is_video: bool) -> InlineKeyboardMarkup:
    actions = ["resize", "crop", "compress"]
    if is_video:
        actions = ["cut", "resize", "crop", "fps", "compress", "strip-audio", "extract-frame"]
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
