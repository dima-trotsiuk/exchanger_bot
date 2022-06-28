from aiogram.dispatcher.filters.state import StatesGroup, State


class ChangeGroupState(StatesGroup):
    id_group = State()

