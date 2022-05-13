from aiogram.dispatcher.filters.state import StatesGroup, State


class NewGroupOrderState(StatesGroup):
    title = State()
