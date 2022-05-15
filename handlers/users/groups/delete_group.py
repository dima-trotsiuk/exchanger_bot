import logging

from aiogram.types import CallbackQuery
from sqlalchemy.orm import sessionmaker

from keyboards.inline.groups.callback_datas import delete_group_buttons_callback
from loader import dp
from utils.db_api.models import engine, Group, Chat


@dp.callback_query_handler(delete_group_buttons_callback.filter(type_command='delete_group'))
async def edit_quantity_call(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=1)
    pk = callback_data.get('pk')

    session = sessionmaker(bind=engine)()
    group = session.query(Group).get(pk)

    chats = session.query(Chat).filter(Chat.group_id == pk)
    if chats:
        for chat in chats:
            chat.group_id = 1
            logging.info(f'Чат "{chat.title}" был перевён в группу "Без группы"')

    session.delete(group)
    session.commit()
    session.close()

    await call.message.answer(f'Група "{group.title}" была удалена')
    await call.message.delete()
    logging.info(f'Удалена с базы група "{group.title}"')
