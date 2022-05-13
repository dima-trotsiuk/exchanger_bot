from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy.orm import sessionmaker

from utils.db_api.models import engine, Chat
from .callback_datas import select_update_chat_buttons_callback


async def select_update_chat_buttons():
    type_command = 'select_update_chat'

    session = sessionmaker(bind=engine)()
    chats = session.query(Chat).order_by(Chat.group_id).all()

    list_button = []

    for chat in chats:
        title = chat.title
        pk = chat.chat_id
        group = chat.group.title
        el = [
            InlineKeyboardButton(
                text=f'{title} - {group}',
                callback_data=select_update_chat_buttons_callback.new(pk=pk, type_command=type_command)
            ),
        ]
        list_button.append(el)
    session.close()
    return InlineKeyboardMarkup(row_width=1, inline_keyboard=list_button)
