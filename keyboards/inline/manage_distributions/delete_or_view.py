from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from .callback_datas import delete_or_view_callback


async def delete_or_view():
    type_command = 'delete_or_view_dist'
    list_button = [
        [
            InlineKeyboardButton(
                text=f'Удалить всю рассылку',
                callback_data=delete_or_view_callback.new(action="delete_all", type_command=type_command)
            ),
        ],
        [
            InlineKeyboardButton(
                text=f'Удалить последнюю рассылку',
                callback_data=delete_or_view_callback.new(action="delete_last", type_command=type_command)
            ),
        ],
        [
            InlineKeyboardButton(
                text=f'Посмотреть последнюю рассылку',
                callback_data=delete_or_view_callback.new(action="view", type_command=type_command)
            ),
        ],
        [
            InlineKeyboardButton(
                text=f'Редактировать последнюю рассылку',
                callback_data=delete_or_view_callback.new(action="edit_last", type_command=type_command)
            ),
        ]
    ]

    return InlineKeyboardMarkup(row_width=1, inline_keyboard=list_button)
