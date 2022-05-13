import logging

from aiogram import types
from sqlalchemy.orm import sessionmaker

from loader import bot, dp
from utils.db_api.models import engine, Chat


@dp.message_handler(content_types=['new_chat_members'])
async def bot_welcome(message: types.Message):
    bot_obj = await bot.get_me()
    bot_id = bot_obj.id

    for chat_member in message.new_chat_members:
        if chat_member.id == bot_id:
            session = sessionmaker(bind=engine)()

            title = message.chat.title
            chat_id = message.chat.id

            # проверяем есть ли в базе такой чат
            flag = session.query(Chat).get(chat_id)
            if flag is None:
                new_chat = Chat(chat_id=chat_id, title=title, group_id=1)
                session.add(new_chat)
                session.commit()
                logging.info(f'Добавлено чат "{title}" в базу данных')
            else:
                logging.info(f'Чат "{title}" уже есть в базе данных')

            session.close()

            await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")


@dp.message_handler(content_types=['left_chat_member'])
async def left_bot(message: types.Message):
    bot_obj = await bot.get_me()
    bot_id = bot_obj.id
    title = message.chat.title
    chat_id = message.chat.id

    if message.left_chat_member.id == bot_id:
        session = sessionmaker(bind=engine)()
        chat = session.query(Chat).get(chat_id)

        session.delete(chat)
        session.commit()
        session.close()

        logging.info(f'Бот вышел из чата "{title}" и был удален из базы')