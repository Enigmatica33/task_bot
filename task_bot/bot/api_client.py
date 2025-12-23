import logging
from datetime import date
from typing import Dict, List, Optional

import aiohttp
from rest_framework import status

from bot.config import config

BASE_URL = config.api.base_url

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


async def get_categories(telegram_user_id: int) -> Optional[List[Dict]]:
    """Получает список категорий пользователя."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{BASE_URL}categories/", params={"user": telegram_user_id}
            ) as response:
                if response.status == status.HTTP_200_OK:
                    return await response.json()

                logging.error(
                    "Ошибка при получении категорий для пользователя "
                    f"{telegram_user_id}: "
                    f"Статус {response.status}, Ответ: {await response.text()}"
                )
                return None
    except aiohttp.ClientError as e:
        logging.error(f"Ошибка клиента AIOHTTP при получении категорий: {e}")
        return None


async def get_tasks(telegram_user_id: int) -> Optional[List[Dict]]:
    """Получает список всех задач пользователя."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{BASE_URL}tasks/", params={"user": telegram_user_id}
            ) as response:
                if response.status == status.HTTP_200_OK:
                    return await response.json()
                logging.error(
                    "Ошибка при получении задач "
                    f"для пользователя {telegram_user_id}: "
                    f"Статус {response.status}, "
                    f"Ответ: {await response.text()}"
                )
                return None
    except aiohttp.ClientError as e:
        logging.error(f"Ошибка при получении списка задач: {e}")
        return None


async def get_task_by_id(task_id: int, user_id: int) -> Optional[Dict]:
    """Получает задачу по её ID."""
    try:
        params = {"user_id": user_id}
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{BASE_URL}tasks/{task_id}/",
                params=params
            ) as response:
                if response.status == status.HTTP_200_OK:
                    return await response.json()
                elif response.status == status.HTTP_404_NOT_FOUND:
                    logging.warning(f"Задача с ID {task_id} не найдена.")
                else:
                    logging.error(
                        f"Ошибка при получении задачи {task_id}: "
                        f"Статус {response.status}, "
                        f"Ответ: {await response.text()}"
                    )
                return None
    except aiohttp.ClientError as e:
        logging.error(f"Ошибка при получении задачи {task_id}: {e}")
        return None


async def add_task(
    telegram_user_id: int,
    title: str,
    category_id: int,
    description: Optional[str] = None,
    due_date: Optional[date] = None,
) -> bool:
    """Добавляет новую задачу."""
    payload = {
        "title": title,
        "category": [category_id],
        "owner_tg_id": telegram_user_id,
    }
    if description:
        payload["description"] = description
    if due_date:
        if isinstance(due_date, str):
            try:
                actual_date = date.fromisoformat(due_date)
            except ValueError:
                logging.error(f"Неверный формат даты в строке: {due_date}")
                return False
        else:
            actual_date = due_date
        payload["due_date"] = actual_date.isoformat()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{BASE_URL}tasks/", json=payload
            ) as response:
                if response.status == status.HTTP_201_CREATED:
                    logging.info(f"Задача '{title}' успешно создана.")
                    return True
                elif response.status == status.HTTP_400_BAD_REQUEST:
                    logging.error(
                        f"Ошибка добавления задачи '{title}': BAD_REQUEST_400."
                        f"Данные: {payload}, Ответ: {await response.text()}"
                    )
                else:
                    logging.error(
                        f"Ошибка добавления задачи '{title}': "
                        f"Статус {response.status}, "
                        f"Ответ: {await response.text()}"
                    )
                return False
    except aiohttp.ClientError as e:
        logging.error(f"Ошибка при добавлении задачи: {e}")
        return False


async def delete_task(task_id: int) -> bool:
    """
    Удаляет задачу по её ID.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                f"{BASE_URL}tasks/{task_id}/"
            ) as response:
                if response.status == status.HTTP_204_NO_CONTENT:
                    logging.info(f"Задача {task_id} успешно удалена.")
                    return True
                elif response.status == status.HTTP_404_NOT_FOUND:
                    logging.warning(
                        f"Не удалось удалить задачу {task_id}: " "не найдена."
                    )
                else:
                    logging.error(
                        f"Ошибка при удалении задачи {task_id}: "
                        f"Статус {response.status}, "
                        f"Ответ: {await response.text()}"
                    )
                return False
    except aiohttp.ClientError as e:
        logging.error(f"Ошибка при удалении задачи {task_id}: {e}")
        return False


async def complete_task(user_id: int, task_id: int) -> bool:
    """
    Отмечает задачу как выполненную.
    """
    payload = {"completed": True}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.patch(
                f"{BASE_URL}tasks/{task_id}/", json=payload
            ) as response:
                if response.status == status.HTTP_200_OK:
                    logging.info(
                        f"Задача {task_id} отмечена как выполненная."
                    )
                    return True
                elif response.status == status.HTTP_404_NOT_FOUND:
                    logging.warning(
                        f"Не удалось завершить задачу {task_id}: "
                        "не найдена."
                    )
                elif response.status == status.HTTP_403_FORBIDDEN:
                    logging.error(
                        f"Пользователь {user_id} не имеет прав "
                        "на завершение задачи {task_id}."
                    )
                else:
                    logging.error(
                        f"Ошибка при завершении задачи {task_id}: "
                        f"Статус {response.status}, "
                        f"Ответ: {await response.text()}"
                    )
                return False
    except aiohttp.ClientError as e:
        logging.error(f"Ошибка при завершении задачи {task_id}: {e}")
        return False
