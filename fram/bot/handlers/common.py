from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from fram.bot import messages

router = Router()


@router.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(messages.welcome())


@router.message(Command("cancel"))
async def cancel_command(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(messages.cancelled())


@router.callback_query(lambda callback: callback.data == "confirm:cancel")
async def cancel_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.answer(messages.cancelled())
    await callback.answer()
