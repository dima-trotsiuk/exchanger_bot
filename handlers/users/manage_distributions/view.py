import logging
from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy import desc
from sqlalchemy.orm import sessionmaker

from keyboards.inline.distributions.callback_datas import get_group_distibutions_button_callback
from keyboards.inline.distributions.get_group import get_group_distibutions_button
from keyboards.inline.manage_distributions.callback_datas import delete_or_view_callback
from keyboards.inline.manage_distributions.delete_or_view import delete_or_view
from loader import dp, bot
from utils.db_api.models import engine, Group, Chat, Message, Message_info


@dp.message_handler(text="Управлять рассылкой 🔧")
async def manage_distributions(message: types.Message):
    await get_group_distibutions_button(message, 'manage_dist', 'Выбери групу:')


@dp.callback_query_handler(
    get_group_distibutions_button_callback.filter(type_command='manage_dist'))
async def manage_distributions_call(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=60)

    await call.message.delete()
    pk_group = callback_data.get("pk")
    session = sessionmaker(bind=engine)()
    group = session.query(Group).get(pk_group)
    title = group.title
    session.close()
    await state.update_data(pk_group_dist=pk_group)
    await call.message.answer(f'Доступные команды: [{title}]', reply_markup=await delete_or_view())


@dp.callback_query_handler(
    delete_or_view_callback.filter(type_command='delete_or_view_dist'))
async def manage_distributions_call(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=2)
    action = callback_data.get("action")

    session = sessionmaker(bind=engine)()

    data = await state.get_data()
    pk_group_dist = data.get("pk_group_dist")

    if action == 'delete_all':
        messages_info = session.query(Message_info).filter(Message_info.group_id == pk_group_dist).all()
        if messages_info:
            for message_info in messages_info:
                messages = session.query(Message).filter(Message.message_info_id == message_info.id).all()
                for message_dist in messages:
                    chat_id = message_dist.chat_id
                    message_id = message_dist.message_id

                    try:
                        await bot.delete_message(chat_id, message_id)
                        logging.info(f'Сообщение {message_id} было удалено с группы {chat_id}')
                    except Exception as e:
                        logging.error(f'Сообщение {message_id} не было удалено с группы {chat_id}, {e}')

                    session.delete(message_dist)
                    session.commit()
                session.delete(message_info)
                session.commit()
            await call.message.answer('Рассылка была удалена')
        else:
            await call.message.answer('Рассылки в данной группе не обнаружено')

    elif action == 'delete_last':
        message_info = session.query(Message_info).filter(Message_info.group_id == pk_group_dist) \
            .order_by(desc(Message_info.id)).limit(1).all()

        if message_info:
            message_info = message_info[0]
            messages = session.query(Message).filter(Message.message_info_id == message_info.id).all()

            for message_dist in messages:
                chat_id = message_dist.chat_id
                message_id = message_dist.message_id

                try:
                    await bot.delete_message(chat_id, message_id)
                    logging.info(f'Сообщение {message_id} было удалено с группы {chat_id}')
                except Exception as e:
                    logging.error(f'Сообщение {message_id} не было удалено с группы {chat_id}, {e}')

                session.delete(message_dist)
                session.commit()
            session.delete(message_info)
            session.commit()

            await call.message.answer('Рассылка была удалена')
        else:
            await call.message.answer('Рассылки в данной группе не обнаружено')


    elif action == 'view':
        message_dist = session.query(Message_info).filter(Message_info.group_id == pk_group_dist) \
            .order_by(desc(Message_info.id)).limit(1).all()
        if message_dist:
            message_dist = message_dist[0]
            message_id = message_dist.message_id
            created = message_dist.created_on

            text_date = f'Время рассылки: {created.year}-{created.month:02}-{created.day:02} ' \
                        f'{created.hour:02}:{created.minute:02}:{created.second:02}'

            await bot.copy_message(chat_id=call.message.chat.id,
                                   message_id=message_id,
                                   from_chat_id=call.message.chat.id)
            await call.message.answer(text_date)
        else:
            await call.message.answer('Сообщение не найдено')
    session.close()
