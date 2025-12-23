import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode, setup_dialogs

from bot.config import config
from bot.dialogs.add_task import add_task_dialog
from bot.dialogs.main_menu import main_menu_dialog
from bot.dialogs.states import MainMenu

logging.basicConfig(level=logging.INFO)


async def start(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(MainMenu.view_tasks, mode=StartMode.RESET_STACK)


async def main():
    bot = Bot(token=config.bot.token)
    dp = Dispatcher()

    dp.include_router(main_menu_dialog)
    dp.include_router(add_task_dialog)
    setup_dialogs(dp)

    dp.message.register(start, CommandStart())

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped")
