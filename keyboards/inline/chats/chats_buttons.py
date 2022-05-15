from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy.orm import sessionmaker

from utils.db_api.models import engine, Chat
from .callback_datas import chats_button_callback


async def chats_button():
    type_command = 'chats'

    session = sessionmaker(bind=engine)()
    without_group = session.query(Chat).filter(Chat.group_id == 1).count()
    with_group = session.query(Chat).filter(Chat.group_id != 1).count()
    session.close()

    list_button = [
        [
            InlineKeyboardButton(
                text=f'Чаты без группы ({without_group})',
                callback_data=chats_button_callback.new(action="without_group", type_command=type_command)
            ),
        ],
        [
            InlineKeyboardButton(
                text=f'Чаты с групой ({with_group})',
                callback_data=chats_button_callback.new(action="with_group", type_command=type_command)
            ),
        ],
        [
            InlineKeyboardButton(
                text=f'Изменить групу',
                callback_data=chats_button_callback.new(action="update", type_command=type_command)
            ),
        ]
    ]

    return InlineKeyboardMarkup(row_width=1, inline_keyboard=list_button)
