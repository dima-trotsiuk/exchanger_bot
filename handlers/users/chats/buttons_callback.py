from aiogram.types import CallbackQuery
from sqlalchemy.orm import sessionmaker

from keyboards.default.cancel import cancel_menu
from keyboards.inline.chats.callback_datas import chats_button_callback
from keyboards.inline.chats.select_update_chat import select_update_chat_buttons
from keyboards.inline.groups.callback_datas import groups_button_callback
from keyboards.inline.groups.delete_groups import delete_group_buttons
from loader import dp
from states.groups.new_group_state import NewGroupOrderState
from utils.db_api.models import engine, Group, Chat


@dp.callback_query_handler(chats_button_callback.filter(type_command='chats'))
async def chat_buttons_call(call: CallbackQuery, callback_data: dict):
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

    elif action == 'update':
        await call.message.answer('Выберите чат, которому нужно присвоить новую группу:',
                                  reply_markup=await select_update_chat_buttons())
    session.close()
