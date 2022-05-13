from aiogram import types

from keyboards.inline.chats.chats_buttons import chats_button
from loader import dp


@dp.message_handler(text="Чаты 💬")
async def chats(message: types.Message):
    await message.answer('Выберите действие:', reply_markup= await chats_button())