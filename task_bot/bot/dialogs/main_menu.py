from datetime import datetime

from aiogram import F
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import (Button, Column, Row, Select, Start,
                                        SwitchTo)
from aiogram_dialog.widgets.text import Const, Format, Jinja, Multi

from bot.api_client import (complete_task, delete_task, get_categories,
                            get_task_by_id, get_tasks)
from bot.dialogs.add_task import on_task_selected
from bot.dialogs.states import AddTask, MainMenu


async def incomplete_tasks_getter(dialog_manager: DialogManager, **kwargs):
    """
    Загружает список невыполненных задач для главного экрана.
    """
    user_id = dialog_manager.event.from_user.id
    tasks = await get_tasks(user_id)
    if not tasks:
        return {"tasks_list": [], "has_tasks": False}
    incomplete_tasks = [task for task in tasks if not task.get("completed")]

    if not incomplete_tasks:
        return {"tasks_list": [], "has_tasks": False}

    dialog_manager.dialog_data["full_tasks_data"] = incomplete_tasks
    all_categories = await get_categories(user_id)
    categories_map = {
        cat["id"]: cat.get("name", "N/A") for cat in all_categories
        }
    tasks_for_buttons = []
    for task in incomplete_tasks:
        category_ids = task.get("category", [])
        category_names = [
            categories_map.get(cat_id)
            for cat_id in category_ids
            if cat_id in categories_map
        ]
        categories_str = ", ".join(category_names) or "без категории"
        tasks_for_buttons.append((task["title"], categories_str, task["id"]))

    return {"tasks_list": tasks_for_buttons, "has_tasks": True}


async def completed_tasks_getter(dialog_manager: DialogManager, **kwargs):
    """
    Загружает список выполненных задач.
    """
    user_id = dialog_manager.event.from_user.id
    tasks = await get_tasks(user_id)
    if not tasks:
        return {"completed_tasks_list": [], "has_completed_tasks": False}
    completed_tasks = [task for task in tasks if task.get("completed")]

    if not completed_tasks:
        return {"completed_tasks_list": [], "has_completed_tasks": False}
    dialog_manager.dialog_data["full_completed_tasks_data"] = completed_tasks
    tasks_for_buttons = [
        (task["title"], task["id"]) for task in completed_tasks
        ]
    return {
        "completed_tasks_list": tasks_for_buttons,
        "has_completed_tasks": True
    }


async def task_details_getter(dialog_manager: DialogManager, **kwargs):
    """Загружает детали выбранной задачи."""
    task_id = dialog_manager.dialog_data.get("task_id")
    user_id = dialog_manager.event.from_user.id
    task = await get_task_by_id(task_id=task_id, user_id=user_id)
    if task is None:
        return {
            "title": "Задача не найдена",
            "description": "Не удалось найти задачу.",
            "category": "N/A",
            "created_at": "N/A",
            "due_date": "N/A",
            "completed": False,
        }
    created_at_val = task.get("created_at")
    created_at_str = "N/A"
    if created_at_val:
        try:
            dt = datetime.fromisoformat(created_at_val.replace("Z", "+00:00"))
            created_at_str = dt.strftime("%d.%m.%Y %H:%M")
        except ValueError:
            created_at_str = created_at_val
    due_date_val = task.get("due_date")
    due_date_str = "не указан"
    if due_date_val:
        try:
            dt = datetime.fromisoformat(due_date_val)
            due_date_str = dt.strftime("%d.%m.%Y")
        except ValueError:
            due_date_str = due_date_val
    all_categories = await get_categories(user_id)
    categories_map = {
        cat["id"]: cat.get("name", "N/A") for cat in all_categories
    }
    category_ids = task.get("category", [])
    category_names = [
        categories_map.get(cat_id)
        for cat_id in category_ids
        if cat_id in categories_map
    ]
    categories_str = ", ".join(category_names) or "без категории"
    return {
        "title": task.get("title", "N/A"),
        "description": task.get("description", "N/A"),
        "category": categories_str,
        "created_at": created_at_str,
        "due_date": due_date_str,
        "completed": task.get("completed", False),
    }


async def on_delete_clicked(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    """
    Обрабатывает нажатие на кнопку удаления задачи.
    """
    task_id = manager.dialog_data.get("task_id")
    user_id = manager.event.from_user.id
    await delete_task(task_id=task_id, user_id=user_id)
    await callback.answer("Задача успешно удалена!")
    await manager.switch_to(MainMenu.view_tasks)


async def on_done_clicked(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    """
    Обрабатывает нажатие на кнопку "Готово", отмечая задачу как выполненную.
    """
    user_id = manager.event.from_user.id
    task_id = manager.dialog_data.get("task_id")
    await complete_task(user_id=user_id, task_id=task_id)
    await callback.answer("Задача отмечена как выполненная!")
    await manager.switch_to(MainMenu.view_tasks)


main_menu_dialog = Dialog(
    Window(
        Format("Привет, {event.from_user.username}!\n"),
        Const("Ваш список активных задач:", when="has_tasks"),
        Const("У вас пока нет задач.", when=~F["has_tasks"]),
        Column(
            Select(
                Format("📝 {item[0]} ({item[1]})"),
                id="task_select",
                item_id_getter=lambda item: item[2],
                items="tasks_list",
                on_click=on_task_selected,
            )
        ),
        Row(
            Start(
                Const("➕ Добавить"),
                id="add_task",
                state=AddTask.select_category
            ),
            SwitchTo(
                Const("✅ Выполненные"),
                id="completed",
                state=MainMenu.view_completed_tasks,
            ),
        ),
        state=MainMenu.view_tasks,
        getter=incomplete_tasks_getter,
    ),
    Window(
        Const("Список выполненных задач:", when="has_completed_tasks"),
        Const("У вас нет выполненных задач.", when=~F["has_completed_tasks"]),
        Column(
            Select(
                Format("✅ {item[0]}"),
                id="completed_task_select",
                item_id_getter=lambda item: item[1],
                items="completed_tasks_list",
                on_click=on_task_selected,
            )
        ),
        SwitchTo(
            Const("⬅️ К активным задачам"),
            id="back_to_active",
            state=MainMenu.view_tasks,
        ),
        state=MainMenu.view_completed_tasks,
        getter=completed_tasks_getter,
    ),
    Window(
        Multi(
            Format("<b>Название:</b> {title}"),
            Format("<b>Описание:</b> {description}"),
            Format("<b>Категория:</b> {category}"),
            Format("<b>Дата создания:</b> {created_at}"),
            Format("<b>Срок выполнения:</b> {due_date}"),
            Jinja(
                "<b>Статус:</b> "
                "{% if completed %}"
                "Выполнена"
                "{% else %}"
                "В процессе"
                "{% endif %}"
            ),
            sep="\n\n",
        ),
        Row(
            SwitchTo(
                Const("⬅️ Назад к списку"),
                id="back_to_main_list",
                state=MainMenu.view_tasks,
            ),
            Button(
                Const("✅ Готово"),
                id="mark_done",
                on_click=on_done_clicked,
                when=~F["completed"],
            ),
            Button(
                Const("🗑️ Удалить"),
                id="delete_task",
                on_click=on_delete_clicked
            ),
        ),
        state=MainMenu.details,
        getter=task_details_getter,
        parse_mode="HTML",
    ),
)
