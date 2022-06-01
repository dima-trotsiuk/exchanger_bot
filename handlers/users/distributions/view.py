import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.orm import sessionmaker

from keyboards.default.cancel import cancel_menu
from keyboards.default.default import default_menu
from keyboards.inline.distributions.callback_datas import get_group_distibutions_button_callback
from keyboards.inline.distributions.get_group import get_group_distibutions_button
from loader import dp, bot
from states.distributions.distributions import DistributionState
from utils.db_api.models import engine, Chat, Message_info, Message, Group


@dp.message_handler(text="Сделать рассылку 📩")
async def distributions(message: types.Message):
    await get_group_distibutions_button(message, 'get_group_dist', 'В какую группу разослать сообщение?')


@dp.callback_query_handler(
    get_group_distibutions_button_callback.filter(type_command='get_group_dist'))
async def get_group_dist_call(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=60)
    pk_group = callback_data.get("pk")
    await call.message.answer('Ожидаю сообщение:', reply_markup=cancel_menu)
    await state.update_data(pk_group=pk_group)
    await DistributionState.photo_or_text.set()


@dp.message_handler(text="Отмена", state=DistributionState.photo_or_text)
async def cancel(message: types.Message, state: FSMContext):
    await message.answer("Хорошо :)", reply_markup=default_menu)
    await state.finish()


@dp.message_handler(state=DistributionState.photo_or_text, content_types=['photo', 'text'])
async def photo_or_text_state(message: types.Message, state: FSMContext):
    content_type = message.content_type

    data = await state.get_data()
    pk_group = data.get("pk_group")

    session = sessionmaker(bind=engine)()
    chats = session.query(Chat).filter(Chat.group_id == pk_group).all()

    if chats:
        chats_pk = []
        if content_type == 'photo':
            caption_flag = False
            try:
                admin_message = await bot.send_photo(message.chat.id, photo=message.photo[-1].file_id,
                                                     caption=message.html_text)
                caption_flag = True
            except TypeError:
                admin_message = await bot.send_photo(message.chat.id, photo=message.photo[-1].file_id)

            m = Message_info(
                message_id=admin_message.message_id,
                group_id=pk_group,
            )
            session.add(m)
            session.commit()

            for chat in chats:
                chats_pk.append(chat.chat_id)
                try:
                    if caption_flag:
                        a = await bot.send_photo(chat.chat_id, photo=message.photo[-1].file_id,
                                                 caption=message.html_text)
                    else:
                        a = await bot.send_photo(chat.chat_id, photo=message.photo[-1].file_id)

                    message_save = Message(
                        message_info_id=m.id,
                        message_id=a.message_id,
                        chat_id=chat.chat_id
                    )
                    session.add(message_save)
                except Exception as e:
                    await message.answer(f'Ошибка при рассылке в чат {chat.chat_id}')
                    logging.error(f'Ошибка при рассылке в чат {chat.chat_id} {e}')

            group = session.query(Group).get(pk_group)
            group_title = group.title
            logging.info(f'В группу "{group_title}" была разослана фотка')

        elif content_type == 'text':
            admin_message = await bot.send_message(message.chat.id, message.html_text)
            m = Message_info(
                message_id=admin_message.message_id,
                group_id=pk_group,
            )
            session.add(m)
            session.commit()

            for chat in chats:
                chats_pk.append(chat.chat_id)
                try:
                    a = await bot.send_message(chat.chat_id, message.html_text)

                    message_save = Message(
                        message_info_id=m.id,
                        message_id=a.message_id,
                        chat_id=chat.chat_id
                    )
                    session.add(message_save)

                    logging.info(f'В чаты {chats_pk} была разослан текст "{a.message_id}"')
                except Exception as e:
                    await message.answer(f'Ошибка при рассылке в чат {chat.chat_id}')
                    logging.error(f'Ошибка при рассылке в чат {chat.chat_id} {e}')

        await message.answer('Сделано 😎', reply_markup=default_menu)
    else:
        await message.answer('В данной группе нету чатов 🤨', reply_markup=default_menu)
    session.commit()
    session.close()
    await state.reset_state()
    await state.finish()
