from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart

from filters.is_admin import IsAdmin
from keyboards.default.default import default_menu
from loader import dp


@dp.message_handler(CommandStart(), IsAdmin())
async def bot_start(message: types.Message):
    await message.answer(f'Привет, {message.from_user.full_name}!', reply_markup=default_menu)



