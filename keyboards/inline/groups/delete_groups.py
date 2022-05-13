from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy.orm import sessionmaker

from utils.db_api.models import engine, Group
from .callback_datas import delete_group_buttons_callback


async def delete_group_buttons():
    type_command = 'delete_group'

    session = sessionmaker(bind=engine)()
    groups = session.query(Group).filter(Group.title != 'Без группы')
    session.close()

    list_button = []

    for group in groups:
        title = group.title
        pk = group.id
        el = [
            InlineKeyboardButton(
                text=f'{title}',
                callback_data=delete_group_buttons_callback.new(pk=pk, type_command=type_command)
            ),
        ]
        list_button.append(el)

    return InlineKeyboardMarkup(row_width=1, inline_keyboard=list_button)
