import logging

from aiogram.types import CallbackQuery
from sqlalchemy.orm import sessionmaker

from keyboards.default.default import default_menu
from keyboards.inline.chats.callback_datas import select_update_group_buttons_callback
from loader import dp
from utils.db_api.models import engine, Chat


@dp.callback_query_handler(select_update_group_buttons_callback.filter(type_command='select_group'))
async def chat_buttons_call(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=1)
    pk_group = callback_data.get('pk_group')
    pk_chat = callback_data.get('pk_chat')

    session = sessionmaker(bind=engine)()
    chat = session.query(Chat).get(pk_chat)
    chat.group_id = pk_group
    session.add(chat)
    session.commit()

    await call.message.answer(f'Чату "{chat.title}" была присвоина группа {chat.group.title}', reply_markup=default_menu)
    await call.message.delete()
    logging.info(f'Чату "{chat.title}" была присвоина группа {chat.group.title}')
    session.close()
