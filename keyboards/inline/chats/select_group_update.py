from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy.orm import sessionmaker

from utils.db_api.models import engine, Group
from .callback_datas import select_update_group_buttons_callback


async def select_update_group_buttons(pk_chat):
    type_command = 'select_group'

    session = sessionmaker(bind=engine)()
    groups = session.query(Group).filter(Group.title != 'Без группы').all()
    session.close()

    list_button = []

    for group in groups:
        title = group.title
        pk_group = group.id

        el = [
            InlineKeyboardButton(
                text=f'{title}',
                callback_data=select_update_group_buttons_callback.new(pk_group=pk_group,
                                                                       pk_chat=pk_chat,
                                                                       type_command=type_command)
            ),
        ]
        list_button.append(el)

    return InlineKeyboardMarkup(row_width=1, inline_keyboard=list_button)
