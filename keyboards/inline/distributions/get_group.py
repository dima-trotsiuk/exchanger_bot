from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy.orm import sessionmaker

from utils.db_api.models import engine, Group, Chat
from .callback_datas import get_group_distibutions_button_callback


async def get_group_distibutions_button():
    type_command = 'get_group_dist'

    session = sessionmaker(bind=engine)()
    groups = session.query(Group).filter(Group.title != 'Без группы')

    list_button = []

    for group in groups:
        title = group.title
        pk = group.id
        count_chats = session.query(Chat).filter(Chat.group_id == group.id).count()
        el = [
            InlineKeyboardButton(
                text=f'{title} ({count_chats})',
                callback_data=get_group_distibutions_button_callback.new(pk=pk, type_command=type_command)
            ),
        ]
        list_button.append(el)
    session.close()
    return InlineKeyboardMarkup(row_width=1, inline_keyboard=list_button)
