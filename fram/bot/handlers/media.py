from pathlib import Path

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message

from fram.bot import messages
from fram.bot.keyboards.actions import (
    cancel_keyboard,
    media_actions_keyboard,
    pipeline_keyboard,
)
from fram.bot.services.files import cleanup_paths, download_media
from fram.bot.services.operations import (
    NO_PARAM_ACTIONS,
    OperationSpecData,
    build_operation,
    build_operations,
    operation_spec,
)
from fram.bot.services.processing import process_for_user
from fram.bot.states.media import MediaFlow
from fram.core.errors import FramError, UnsupportedFormat
from fram.core.media import MediaType
from fram.core.operations import Operation

router = Router()


@router.message(F.document | F.video | F.photo)
async def media_received(message: Message, bot: Bot, state: FSMContext) -> None:
    try:
        media = await download_media(message, bot)
    except UnsupportedFormat:
        await message.answer(messages.unsupported())
        return

    await state.set_state(MediaFlow.choosing_action)
    await state.update_data(
        input_path=str(media.path),
        media_type=media.media_type.value,
        filename=media.filename,
        operations=[],
    )
    await message.answer(
        messages.media_loaded(media.filename, media.media_type),
        reply_markup=media_actions_keyboard(is_video=media.media_type == MediaType.VIDEO),
    )


@router.callback_query(MediaFlow.choosing_action, F.data.startswith("action:"))
async def action_selected(callback: CallbackQuery, state: FSMContext) -> None:
    action = _callback_value(callback.data, "action:")
    data = await state.get_data()
    media_type = MediaType(data["media_type"])

    await state.update_data(action=action)
    if action in NO_PARAM_ACTIONS:
        operation = operation_spec(action)
        await _add_operation_spec(state, operation)
        await state.set_state(MediaFlow.choosing_next)
        data = await state.get_data()
        await callback.message.answer(messages.operation_added(len(data["operations"])))
        await callback.message.answer(
            "Add another operation or run now.",
            reply_markup=pipeline_keyboard(),
        )
        await callback.answer()
        return

    await state.set_state(MediaFlow.entering_params)
    await callback.message.answer(
        messages.action_prompt(action, media_type),
        reply_markup=cancel_keyboard(),
    )
    await callback.answer()


@router.callback_query(MediaFlow.choosing_next, F.data == "pipeline:add")
async def add_another_operation(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    media_type = MediaType(data["media_type"])
    await state.set_state(MediaFlow.choosing_action)
    await callback.message.answer(
        "Choose the next operation.",
        reply_markup=media_actions_keyboard(is_video=media_type == MediaType.VIDEO),
    )
    await callback.answer()


@router.callback_query(MediaFlow.choosing_next, F.data == "pipeline:run")
async def run_operation_pipeline(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    media_type = MediaType(data["media_type"])
    try:
        operations = build_operations(_operation_specs(data), media_type)
    except FramError as exc:
        await callback.message.answer(messages.invalid_input(str(exc)))
        await callback.answer()
        return

    await _process_and_send(callback.message, state, operations)
    await callback.answer()


@router.message(MediaFlow.entering_params)
async def params_received(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    action = data["action"]
    media_type = MediaType(data["media_type"])

    try:
        build_operation(action, media_type, message.text)
    except FramError as exc:
        await message.answer(messages.invalid_input(str(exc)), reply_markup=cancel_keyboard())
        return

    await _add_operation_spec(state, operation_spec(action, message.text))
    data = await state.get_data()
    await state.set_state(MediaFlow.choosing_next)
    await message.answer(messages.operation_added(len(data["operations"])))
    await message.answer("Add another operation or run now.", reply_markup=pipeline_keyboard())


async def _process_and_send(
    message: Message | None,
    state: FSMContext,
    operations: list[Operation],
) -> None:
    if message is None:
        return

    data = await state.get_data()
    input_path = data["input_path"]
    await state.set_state(MediaFlow.processing)
    status_message = await message.answer(messages.processing())

    output_path = None
    try:
        output_path = process_for_user(input_path=Path(input_path), operations=operations)
        await message.answer_document(FSInputFile(output_path), caption=messages.done())
    except FramError as exc:
        await message.answer(messages.invalid_input(str(exc)))
    finally:
        cleanup_paths(Path(input_path), output_path)
        await state.clear()
        await status_message.delete()


def _callback_value(data: str | None, prefix: str) -> str:
    if not data or not data.startswith(prefix):
        raise ValueError("Invalid callback data.")
    return data.removeprefix(prefix)


async def _add_operation_spec(state: FSMContext, operation: OperationSpecData) -> None:
    data = await state.get_data()
    operations = [*_operation_specs(data), operation]
    await state.update_data(operations=operations)


def _operation_specs(data: dict[str, object]) -> list[OperationSpecData]:
    operations = data.get("operations", [])
    if not isinstance(operations, list):
        return []
    return operations
