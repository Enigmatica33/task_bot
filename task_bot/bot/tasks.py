import asyncio
import logging

from aiogram import Bot
from celery import Celery

from .config import config

logger = logging.getLogger(__name__)

celery_app = Celery("proj", broker=config.redis.dsn, backend=config.redis.dsn)


async def _send_notification(user_id: int, task_title: str):
    """
    Внутренняя асинхронная функция для отправки уведомления.
    """
    async with Bot(token=config.bot.token) as bot:
        text = (
            "🔔 НАПОМИНАНИЕ!\n\nСегодня срок выполнения вашей задачи: "
            f"«{task_title}»"
        )
        await bot.send_message(chat_id=user_id, text=text)


@celery_app.task
def send_task_notification(user_id: int, task_title: str):
    """
    Синхронная задача Celery для отправки уведомления.
    """
    logger.info(
        f"Запускаю отправку уведомления для задачи «{task_title}»"
        f" пользователю {user_id}..."
    )
    status = "failure"
    error_info = None
    try:
        asyncio.run(_send_notification(user_id, task_title))
        logger.info(
            f"Уведомление для пользователя {user_id} "
            "успешно отправлено.")
        status = "success"
    except Exception as e:
        logger.error(
            f"Ошибка при отправке уведомления пользователю {user_id}: {e}",
            exc_info=True,
        )
        error_info = str(e)

    logger.info(
        "Задача send_task_notification для пользователя "
        f"{user_id} завершена."
    )
    return {"status": status, "user_id": user_id, "error": error_info}
