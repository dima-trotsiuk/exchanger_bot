from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

cancel_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Отмена"),
        ],

    ],
    resize_keyboard=True

)
