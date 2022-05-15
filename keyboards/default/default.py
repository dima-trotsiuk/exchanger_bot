from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

default_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Группы 👥"),
            KeyboardButton(text="Чаты 💬"),
        ],
        [
            KeyboardButton(text="Сделать рассылку 📩"),
            KeyboardButton(text="Сделать опрос ❔",
                           request_poll=types.KeyboardButtonPollType(type=types.PollType.REGULAR))
        ],
    ],
    resize_keyboard=True

)