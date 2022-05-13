from aiogram import types

from loader import dp


@dp.message_handler(text="Чаты 💬")
async def get_storage_func(message: types.Message):
    pass