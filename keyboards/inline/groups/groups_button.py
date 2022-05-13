from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from .callback_datas import groups_button_callback


async def groups_button():
    type_command = 'groups'
    list_button = [
        [
            InlineKeyboardButton(
                text=f'Создать группу',
                callback_data=groups_button_callback.new(action="create", type_command=type_command)
            ),
            InlineKeyboardButton(
                text=f'Посмотреть',
                callback_data=groups_button_callback.new(action="view", type_command=type_command)
            ),
            InlineKeyboardButton(
                text=f'Удалить группу',
                callback_data=groups_button_callback.new(action="delete", type_command=type_command)
            ),
        ]
    ]

    return InlineKeyboardMarkup(row_width=1, inline_keyboard=list_button)
