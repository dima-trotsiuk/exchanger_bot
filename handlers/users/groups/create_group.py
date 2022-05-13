import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from sqlalchemy.orm import sessionmaker

from keyboards.default.default import default_menu
from loader import dp
from states.groups.new_group_state import NewGroupOrderState
from utils.db_api.models import engine, Group


@dp.message_handler(text="Отмена", state=NewGroupOrderState.title)
async def cancel(message: types.Message, state: FSMContext):
    await message.answer("Хорошо :)", reply_markup=default_menu)
    await state.finish()


@dp.message_handler(state=NewGroupOrderState.title)
async def create_state(message: types.Message, state: FSMContext):
    title = message.text

    session = sessionmaker(bind=engine)()
    new_group = Group(title=title)
    session.add(new_group)
    session.commit()
    session.close()

    await message.answer(f'Создано новую группу "{title}"', reply_markup=default_menu)
    logging.info(f'Создано новую группу "{title}"')
    await state.finish()
