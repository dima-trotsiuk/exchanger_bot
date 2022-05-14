from aiogram.dispatcher.filters.state import StatesGroup, State


class DistributionState(StatesGroup):
    photo_or_text = State()
