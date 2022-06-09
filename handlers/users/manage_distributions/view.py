import logging
from datetime import datetime, timedelta

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram.utils.exceptions import MessageToEditNotFound, BadRequest
from sqlalchemy import desc
from sqlalchemy.orm import sessionmaker

from keyboards.default.cancel import cancel_menu
from keyboards.default.default import default_menu
from keyboards.inline.distributions.callback_datas import get_group_distibutions_button_callback
from keyboards.inline.distributions.get_group import get_group_distibutions_button
from keyboards.inline.manage_distributions.callback_datas import delete_or_view_callback
from keyboards.inline.manage_distributions.delete_or_view import delete_or_view
from loader import dp, bot
from states.manage_distributions.edit_message_state import EditMessageState
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
    elif action == 'edit_last':
        now_date = datetime.now()
        two_weeks_ago = now_date - timedelta(days=13)
        last_message = session.query(Message_info) \
            .filter(Message_info.group_id == pk_group_dist, Message_info.created_on > two_weeks_ago) \
            .order_by(desc(Message_info.id)).limit(1).all()
        if last_message:
            last_message = last_message[0]
            message_id = last_message.message_id
            created = last_message.created_on

            text_date = f'Время рассылки: {created.year}-{created.month:02}-{created.day:02} ' \
                        f'{created.hour:02}:{created.minute:02}:{created.second:02}'
            await bot.copy_message(chat_id=call.message.chat.id,
                                   message_id=message_id,
                                   from_chat_id=call.message.chat.id)
            await call.message.answer(text_date)

            await call.message.answer(f'Введите новое отредактированое сообщение:', reply_markup=cancel_menu)

            await state.update_data(id_message_main=last_message.id)

            await EditMessageState.edit_message.set()
        else:
            await call.message.answer(f'Сообщений не найдено либо истек срок изменения')

    session.close()


@dp.message_handler(text="Отмена", state=EditMessageState.edit_message)
async def cancel(message: types.Message, state: FSMContext):
    await message.answer("Хорошо :)", reply_markup=default_menu)
    await state.finish()


@dp.message_handler(state=EditMessageState.edit_message, content_types=['photo', 'text'])
async def edit_message_state(message: types.Message, state: FSMContext):
    content_type = message.content_type
    text_html = message.html_text

    data = await state.get_data()
    id_message_main = data.get('id_message_main')

    session = sessionmaker(bind=engine)()
    changed_messages = session.query(Message).filter(Message.message_info_id == id_message_main).all()
    main_message = session.query(Message_info).get(id_message_main)
    main_message.message_id = message.message_id
    flag = True
    if content_type == 'text':
        for changed_message in changed_messages:
            chat_id = changed_message.chat_id
            message_id = changed_message.message_id

            try:
                await bot.edit_message_text(text=text_html,
                                            chat_id=chat_id,
                                            message_id=message_id)

            except MessageToEditNotFound:
                chat = session.query(Chat).get(Chat.id == chat_id)
                logging.error(f'Не найдено изменяемое сообщение message_id = {message_id}, chat = {chat.title}')
                await message.answer(f'Не смог обновить сообщение в чате {chat.title}')
            except BadRequest:
                flag = False
                await message.answer(f'Не могу преобразовать фотку в текст!!!', reply_markup=default_menu)
                break
        if flag:
            await message.answer(f'Сообщения изменены', reply_markup=default_menu)
    elif content_type == 'photo':
        photo_media = InputMediaPhoto(message.photo[-1].file_id)
        for changed_message in changed_messages:
            chat_id = changed_message.chat_id
            message_id = changed_message.message_id
            try:
                await bot.edit_message_media(media=photo_media,
                                             chat_id=chat_id,
                                             message_id=message_id)
                await bot.edit_message_caption(chat_id=chat_id,
                                               message_id=message_id,
                                               caption=text_html)

            except BadRequest:
                flag = False
                await message.answer(f'Не могу преобразовать текст в фотку!!!', reply_markup=default_menu)
                break
        if flag:
            await message.answer(f'Сообщения изменены', reply_markup=default_menu)
    if flag:
        session.add(main_message)
        session.commit()
    session.close()

    await state.finish()
