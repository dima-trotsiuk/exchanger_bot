import logging

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
from utils.db_api.models import engine, Message, Group, Chat


@dp.message_handler(text="Управлять рассылкой 🔧")
async def manage_distributions(message: types.Message):
    await message.answer('В разработке')
    # await get_group_distibutions_button(message, 'manage_dist', 'Выбери групу:')
    # session = sessionmaker(bind=engine)()
    # messages = session.query(Message).filter(Message.group_id == 2).all()
    # for message_dist in messages:
    #     chat_id = message_dist.chat_id
    #     message_id = message_dist.message_id
    #     # flag = await bot.delete_message(chat_id, message_id)
    #     a = await bot.copy_message(chat_id=message.chat.id,
    #                                message_id=message_id,
    #                                from_chat_id=chat_id)
    #     print(a)
    #     print(dir(a))
    #     # if flag:
    #     #     logging.info(f'Сообщение {message_id} было удалено с группы {chat_id}')
    #     # else:
    #     #     logging.error(f'Сообщение {message_id} не было удалено с группы {chat_id}')
    # session.close()


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
    await call.answer(cache_time=60)
    action = callback_data.get("action")

    session = sessionmaker(bind=engine)()

    data = await state.get_data()
    pk_group_dist = data.get("pk_group_dist")

    if action == 'delete_all':
        messages = session.query(Message).filter(Message.group_id == pk_group_dist).all()
        for message_dist in messages:
            chat_id = message_dist.chat_id
            message_id = message_dist.message_id

            message_dist.delete()
            session.commit()

            flag = await bot.delete_message(chat_id, message_id)

            if flag:
                logging.info(f'Сообщение {message_id} было удалено с группы {chat_id}')
            else:
                logging.error(f'Сообщение {message_id} не было удалено с группы {chat_id}')

    elif action == 'delete_last':
        await call.message.answer('delete_last')

    elif action == 'view':
        message_dist = session.query(Message).filter(Message.group_id == pk_group_dist) \
            .order_by(desc(Message.id)).limit(1).all()
        if message_dist:
            message_dist = message_dist[0]
            message_id = message_dist.message_id

            await bot.copy_message(chat_id=call.message.chat.id,
                                   message_id=message_id,
                                   from_chat_id=call.message.chat.id)
        else:
            await call.message.answer('Сообщение не найдено')
    session.close()
