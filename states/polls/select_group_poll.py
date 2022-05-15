from aiogram.dispatcher.filters.state import StatesGroup, State


class SelectGroupPollState(StatesGroup):
    group = State()
