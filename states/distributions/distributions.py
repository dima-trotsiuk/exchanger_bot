from aiogram.dispatcher.filters.state import StatesGroup, State


class DistributionState(StatesGroup):
    delayed = State()
    delay_date = State()
    photo_or_text = State()
