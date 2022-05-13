from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

default_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Группы 👥"),
            KeyboardButton(text="Чаты 💬"),
        ],
        [
            KeyboardButton(text="Сделать рассылку 📩"),
            KeyboardButton(text="Сделать опрос ❔")
        ],
    ],
    resize_keyboard=True

)