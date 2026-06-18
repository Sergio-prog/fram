from aiogram.fsm.state import State, StatesGroup


class MediaFlow(StatesGroup):
    waiting_for_media = State()
    choosing_action = State()
    entering_params = State()
    choosing_next = State()
    processing = State()
