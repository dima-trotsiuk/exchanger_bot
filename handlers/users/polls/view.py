from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType, CallbackQuery
from sqlalchemy.orm import sessionmaker

from keyboards.inline.distributions.callback_datas import get_group_distibutions_button_callback
from keyboards.inline.distributions.get_group import get_group_distibutions_button
from loader import dp, bot
from utils.db_api.models import engine, Chat


@dp.message_handler(content_types=ContentType.POLL)
async def poll(message: types.Message, state: FSMContext):
    message_poll = message.poll

    options = message_poll.options
    options_list = []
    for el in options:
        options_list.append(el['text'])
    question = message_poll.question
    is_anonymous = message_poll.is_anonymous

    message_poll_dict = {'question': question, 'options': options_list, 'is_anonymous': is_anonymous}

    await state.update_data(message_poll_dict=message_poll_dict)
    await get_group_distibutions_button(message, 'select_group_poll', 'В какую групу разослать опрос?')


@dp.callback_query_handler(
    get_group_distibutions_button_callback.filter(type_command='select_group_poll'))
async def get_group_dist_call(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=60)
    await call.message.delete()
    pk_group = callback_data.get("pk")

    data = await state.get_data()
    message_poll_dict = data.get("message_poll_dict")

    question = message_poll_dict['question']
    options = message_poll_dict['options']
    is_anonymous = message_poll_dict['is_anonymous']

    session = sessionmaker(bind=engine)()
    chats = session.query(Chat).filter(Chat.group_id == pk_group).all()
    session.close()

    if chats:
        for chat in chats:
            await bot.send_poll(chat_id=chat.chat_id,
                                question=question,
                                options=options,
                                is_anonymous=is_anonymous)
