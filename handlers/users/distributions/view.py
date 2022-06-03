import asyncio
import logging
from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.orm import sessionmaker

from keyboards.default.cancel import cancel_menu
from keyboards.default.default import default_menu
from keyboards.default.delated_quiz import delated_quiz_buttons
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
    await state.update_data(pk_group=pk_group)

    await call.message.answer(f'Сообщение будет отложенное?', reply_markup=delated_quiz_buttons)
    await DistributionState.delayed.set()


@dp.message_handler(text="Отмена", state=[DistributionState.delayed,
                                          DistributionState.photo_or_text,
                                          DistributionState.delay_date])
async def cancel(message: types.Message, state: FSMContext):
    await message.answer("Хорошо :)", reply_markup=default_menu)
    await state.finish()


@dp.message_handler(text="Отправить сейчас 📩", state=DistributionState.delayed)
async def send_now(message: types.Message):
    await message.answer('Ожидаю сообщение:', reply_markup=cancel_menu)
    await DistributionState.photo_or_text.set()


@dp.message_handler(text="Отложенное ⏱", state=DistributionState.delayed)
async def send_delayed(message: types.Message):
    await message.answer(f'Введи дату и время в формате 22.12.2022 22:00', reply_markup=cancel_menu)
    await DistributionState.delay_date.set()


@dp.message_handler(state=DistributionState.delay_date)
async def delay_date(message: types.Message, state: FSMContext):
    date = message.text
    try:
        delay_data = datetime.strptime(date, '%d.%m.%Y %H:%M')
        now_data = datetime.now()

        if now_data < delay_data:
            await state.update_data(delay_data=delay_data)

            await message.answer('Ожидаю сообщение:', reply_markup=cancel_menu)
            await DistributionState.photo_or_text.set()
        else:
            await message.answer(f'Не могу сделать рассылку в прошлое. Введи новую дату.', reply_markup=cancel_menu)

    except ValueError:
        await message.answer(f'Введи дату в формате 01.12.2022 15:00!!', reply_markup=cancel_menu)


@dp.message_handler(state=DistributionState.photo_or_text, content_types=['photo', 'text'])
async def photo_or_text_state(message: types.Message, state: FSMContext):
    data = await state.get_data()
    pk_group = data.get('pk_group')
    delay_data = data.get('delay_data')

    if delay_data is not None:

        await state.reset_state()
        await state.finish()

        now_data = datetime.now()
        if now_data > delay_data:
            await message.answer(f'Не могу сделать рассылку в прошлое. Сделай рассылку заново.',
                                 reply_markup=default_menu)
        else:
            sleep_time = (delay_data - now_data).seconds

            await message.answer(f'Это сообщение будет разослано в {delay_data.strftime("%d.%m.%Y %H:%M")}',
                                 reply_markup=default_menu)
            await asyncio.sleep(sleep_time)
            await message.answer('Было разослано отложенное сообщение 🤩')
            await send_message_func(message, pk_group, delay_data)
    else:
        await send_message_func(message, pk_group, delay_data)

        await state.reset_state()
        await state.finish()


async def send_message_func(message, pk_group, delay_data=None):
    content_type = message.content_type

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
                except Exception as e:
                    await message.answer(f'Ошибка при рассылке в чат {chat.chat_id}')
                    logging.error(f'Ошибка при рассылке в чат {chat.chat_id} {e}')

            group = session.query(Group).get(pk_group)
            group_title = group.title
            logging.info(f'В группу "{group_title}" был разослан текст')

        await message.answer('Сделано 😎', reply_markup=default_menu)

    else:
        await message.answer('В данной группе нету чатов 🤨', reply_markup=default_menu)
    session.commit()
    session.close()
