from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from fram.core.action_registry import ACTION_BY_NAME, actions_for_media
from fram.core.media import MediaType

ACTION_LABELS = {name: spec.bot_label for name, spec in ACTION_BY_NAME.items()}


def media_actions_keyboard(is_video: bool) -> InlineKeyboardMarkup:
    media_type = MediaType.VIDEO if is_video else MediaType.IMAGE
    actions = actions_for_media(media_type)
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


def pipeline_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Add operation", callback_data="pipeline:add")],
            [InlineKeyboardButton(text="✅ Run pipeline", callback_data="pipeline:run")],
            [InlineKeyboardButton(text="↩️ Cancel", callback_data="confirm:cancel")],
        ]
    )
