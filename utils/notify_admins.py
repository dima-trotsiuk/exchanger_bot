import logging

from aiogram import Dispatcher

from data.config import admins


async def on_startup_notify(dp: Dispatcher):

    try:
        await dp.bot.send_message(admins[0], "Бот Запущен и готов к работе")

    except Exception as err:
        logging.exception(err)
