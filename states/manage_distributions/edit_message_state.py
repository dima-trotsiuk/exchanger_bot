from aiogram.dispatcher.filters.state import StatesGroup, State


class EditMessageState(StatesGroup):
    edit_message = State()
