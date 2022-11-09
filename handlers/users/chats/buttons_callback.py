import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.exceptions import ChatNotFound
from sqlalchemy.orm import sessionmaker

from keyboards.default.cancel import cancel_menu
from keyboards.default.default import default_menu
from keyboards.inline.chats.callback_datas import chats_button_callback
from keyboards.inline.chats.select_group_update import select_update_group_buttons
from loader import dp, bot
from states.chats.change_group_state import ChangeGroupState
from utils.db_api.models import engine, Group, Chat


@dp.callback_query_handler(chats_button_callback.filter(type_command='chats'))
async def chat_buttons_call(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=1)
    action = callback_data.get('action')
    session = sessionmaker(bind=engine)()

    if action == 'without_group':
        flag = session.query(Chat).filter(Chat.group_id == 1).count()
        if flag:
            chats = session.query(Chat).filter(Chat.group_id == 1).all()
            text = 'Чаты без группы:\n\n'
            for chat in chats:
                text += f'{chat.title}\n'

            await call.message.answer(text)
        else:
            await call.message.answer('Нету таких чатов')

    elif action == 'with_group':
        flag = session.query(Chat).filter(Chat.group_id != 1).count()
        if flag:
            groups = session.query(Group).filter(Group.title != 'Без группы')
            text = ''
            for group in groups:
                text += f'<b>{group.title}</b>\n\n'
                pk = group.id
                chats = session.query(Chat).filter(Chat.group_id == pk).all()

                for i, chat in enumerate(chats, start=1):
                    text += f'{i}. {chat.title}\n'
                text += '\n'
            await call.message.answer(text)
        else:
            await call.message.answer('Нету таких чатов')

    elif action == 'change_group':
        await change_group(call, state)

    elif action == 'update_chats':
        chats = session.query(Chat).all()
        updated_flag = True
        for chat in chats:
            try:
                new_chat_title = await bot.get_chat(chat.chat_id)
                new_chat_title = new_chat_title.title
                current_chat_title = chat.title

                if new_chat_title != current_chat_title:
                    updated_flag = False
                    chat.title = new_chat_title
                    session.add(chat)

                    await call.message.answer(f'Назва чату "{current_chat_title}" была обновлена в "{new_chat_title}"')
                    logging.info(f'Назва чату "{current_chat_title}" была обновлена в "{new_chat_title}"')
            except ChatNotFound:
                session.delete(chat)
                await call.message.answer(f'Чат "{chat.title}" был не найден. '
                                          f'Возможно его удалили или бот был исключен.'
                                          f'Этот чат удален с базы данных.')
                logging.info(f'Чат "{chat.title}" был удален с базы при попытке обновить данные')

        if updated_flag:
            await call.message.answer(f'Информация о чатах актуальная, обновлять не нужно')

        session.commit()
    session.close()


async def change_group(call, state):
    session = sessionmaker(bind=engine)()
    chats = session.query(Chat).order_by(Chat.group_id).all()

    text = 'Выберите чат, которому нужно присвоить новую группу:\n\n'
    group_dict = {}
    i = 0
    for chat in chats:
        i += 1
        title = chat.title
        group_dict[i] = chat.chat_id

        group = chat.group.title
        text += f'<b>{i}.</b> <i>"{title}"</i> - {group}\n'
        if i % 50 == 0:
            await call.message.answer(text)
            text = ''

    await state.update_data(group_dict=group_dict)
    session.close()
    await call.message.answer(text, reply_markup=cancel_menu)

    await ChangeGroupState.id_group.set()


@dp.message_handler(text="Отмена", state=ChangeGroupState.id_group)
async def cancel(message: types.Message, state: FSMContext):
    await message.answer("Хорошо :)", reply_markup=default_menu)
    await state.finish()


@dp.message_handler(state=ChangeGroupState.id_group)
async def s1(message: types.Message, state: FSMContext):
    id_chat = message.text

    data = await state.get_data()

    group_dict = data.get('group_dict')

    if id_chat.isdigit():
        id_chat = int(id_chat)
        if id_chat in group_dict:
            await state.finish()
            await message.answer('В какую группу присвоить чат?',
                                 reply_markup=await select_update_group_buttons(pk_chat=group_dict[int(id_chat)]))
        else:
            await state.finish()
            await message.answer('Такого чату нету', reply_markup=default_menu)
    else:
        await state.finish()
        await message.answer('Нужно ввести число!', reply_markup=default_menu)


