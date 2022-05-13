from aiogram.types import CallbackQuery
from sqlalchemy.orm import sessionmaker

from keyboards.default.cancel import cancel_menu
from keyboards.inline.groups.callback_datas import groups_button_callback
from keyboards.inline.groups.delete_groups import delete_group_buttons
from loader import dp
from states.groups.new_group_state import NewGroupOrderState
from utils.db_api.models import engine, Group


@dp.callback_query_handler(groups_button_callback.filter(type_command='groups'))
async def group_buttons_call(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=1)
    action = callback_data.get('action')
    session = sessionmaker(bind=engine)()

    if action == 'create':
        await NewGroupOrderState.title.set()
        await call.message.answer('Введите название новой группы:', reply_markup=cancel_menu)
    elif action == 'delete':

        groups_count = session.query(Group).filter(Group.title != 'Без группы').count()

        if groups_count > 0:
            await call.message.answer('Нажмите на группу, которую хотите удалить:',
                                      reply_markup=await delete_group_buttons())
        else:
            await call.message.answer('Групп нету, создайте их')
    elif action == 'view':
        groups = session.query(Group).filter(Group.title != 'Без группы').all()
        if len(groups) > 0:
            text = 'Список групп:\n\n'
            for group in groups:
                text += f'{group.title}\n'
            await call.message.answer(text)
        else:
            await call.message.answer('Групп нету, создайте их')
    session.close()
