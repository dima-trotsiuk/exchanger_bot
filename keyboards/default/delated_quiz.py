from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

delated_quiz_buttons = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Отложенное ⏱"),
        ],
        [
            KeyboardButton(text="Отправить сейчас 📩"),
        ],
        [
            KeyboardButton(text="Отмена"),
        ],


    ],
    resize_keyboard=True

)
