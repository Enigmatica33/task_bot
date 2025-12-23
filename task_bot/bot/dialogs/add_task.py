from datetime import date, datetime
from typing import Union

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import (Back, Button, Calendar, Column, Group,
                                        Select, Start, SwitchTo)
from aiogram_dialog.widgets.text import Const, Format

from bot.api_client import add_task, get_categories

from .states import AddTask, MainMenu


async def on_task_selected(
    callback: CallbackQuery,
    widget: Select,
    manager: DialogManager,
    item_id: str,
):
    """Сохраняет ID выбранной задачи и переключает на окно деталей."""
    manager.dialog_data["task_id"] = int(item_id)
    await manager.switch_to(MainMenu.details)


async def categories_getter(dialog_manager: DialogManager, **kwargs):
    """Загружает категории для выбора."""
    categories = await get_categories(
        telegram_user_id=dialog_manager.event.from_user.id
    )
    dialog_manager.dialog_data["full_categories_list"] = categories
    category_list = [(cat["name"], cat["id"]) for cat in categories]
    return {"categories": category_list}


async def success_getter(dialog_manager: DialogManager, **kwargs):
    """Подготавливает данные для финального экрана."""
    due_date = dialog_manager.dialog_data.get("task_due_date")
    due_date_str = "не указан"
    if due_date:
        due_date_str = date.fromisoformat(due_date).strftime("%d.%m.%Y")

    return {
        "title": dialog_manager.dialog_data.get("task_title", "Без названия"),
        "category": dialog_manager.dialog_data.get(
            "category_name",
            "Без категории"
        ),
        "due_date": due_date_str,
    }


async def on_category_selected(
    callback: CallbackQuery,
    widget: Select,
    manager: DialogManager,
    item_id: str
):
    """
    Сохраняет выбранную категорию (ID и название)
    и переключает на ввод названия.
    """
    manager.dialog_data["category_id"] = int(item_id)
    full_categories = manager.dialog_data.get("full_categories_list", [])
    for category in full_categories:
        if str(category["id"]) == item_id:
            manager.dialog_data["category_name"] = category["name"]
            break
    await manager.switch_to(AddTask.input_title)


async def on_title_entered(
    message: Message, widget: MessageInput, manager: DialogManager
):
    """Сохраняет название задачи и переключает на ввод описания."""
    manager.dialog_data["task_title"] = message.text
    await manager.switch_to(AddTask.input_description)


async def on_description_entered(
    message: Message,
    widget: MessageInput,
    manager: DialogManager,
):
    """Сохраняет описание задачи и переключает на выбор даты."""
    manager.dialog_data["task_description"] = message.text
    await manager.switch_to(AddTask.input_due_date)


async def save_task(
        manager: DialogManager,
        event: Union[CallbackQuery, Message]):
    """Централизованная функция для сохранения задачи."""
    from ..tasks import send_task_notification

    user_id = manager.event.from_user.id
    title = manager.dialog_data.get("task_title")
    due_date_str = manager.dialog_data.get("task_due_date")
    success = await add_task(
        telegram_user_id=user_id,
        title=title,
        category_id=manager.dialog_data.get("category_id"),
        description=manager.dialog_data.get("task_description"),
        due_date=due_date_str,
    )
    if success:
        if due_date_str:
            notification_time = datetime.fromisoformat(due_date_str).replace(
                hour=19, minute=00
            )
            send_task_notification.apply_async(
                args=[user_id, title], eta=notification_time
            )
        await manager.switch_to(AddTask.success)
    else:
        error_message = "❌ Ошибка при добавлении задачи."
        if isinstance(event, CallbackQuery):
            await event.message.answer(error_message)
        else:
            await event.answer(error_message)
        await manager.done()


async def on_due_date_entered(
    callback: CallbackQuery,
    widget: Calendar,
    manager: DialogManager,
    selected_date: date,
):
    """Сохраняет выбранную дату и вызывает функцию сохранения."""
    manager.dialog_data["task_due_date"] = selected_date.isoformat()
    await save_task(manager, callback)


async def on_skip_due_date(
    callback: CallbackQuery,
    widget: Button,
    manager: DialogManager,
):
    """Обнуляет дату и вызывает функцию сохранения."""
    manager.dialog_data["task_due_date"] = None
    await save_task(manager, callback)


add_task_dialog = Dialog(
    Window(
        Const("Выберите категорию для новой задачи:"),
        Group(
            Select(
                Format("{item[0]}"),
                id="select_category",
                item_id_getter=lambda item: item[1],
                items="categories",
                on_click=on_category_selected,
            ),
            width=2,
        ),
        Start(
            Const("⬅️ Назад"),
            id="back_to_main_menu",
            state=MainMenu.view_tasks
        ),
        getter=categories_getter,
        state=AddTask.select_category,
    ),
    Window(
        Const("Теперь введите название задачи:"),
        MessageInput(on_title_entered),
        Back(Const("⬅️ Назад")),
        state=AddTask.input_title,
    ),
    Window(
        Const("Введите описание (опционально):"),
        MessageInput(on_description_entered),
        Column(
            SwitchTo(
                Const("Пропустить"),
                id="skip_description",
                state=AddTask.input_due_date
            ),
            Back(Const("⬅️ Назад")),
        ),
        state=AddTask.input_description,
    ),
    Window(
        Const("Выберите дату выполнения (опционально):"),
        Calendar(id="due_date_calendar", on_click=on_due_date_entered),
        Column(
            Button(
                Const("Пропустить и сохранить"),
                id="skip_and_save",
                on_click=on_skip_due_date,
            ),
            Back(Const("⬅️ Назад")),
        ),
        state=AddTask.input_due_date,
    ),
    Window(
        Format(
            "Задача «{title}» успешно добавлена.\n"
            "Категория - {category}, срок выполнения - {due_date}."
        ),
        Column(
            Start(
                Const("Посмотреть мой список задач"),
                id="view_tasks_btn",
                state=MainMenu.view_tasks,
            ),
            Start(
                Const("➕ Добавить новую задачу"),
                id="add_another_task_btn",
                state=AddTask.select_category,
            ),
        ),
        state=AddTask.success,
        getter=success_getter,
        parse_mode="HTML",
    ),
)
