from aiogram import types

from keyboards.inline.groups.groups_button import groups_button
from loader import dp


@dp.message_handler(text="Группы 👥")
async def get_storage_func(message: types.Message):
    await message.answer('Выберите действие:', reply_markup=await groups_button())
