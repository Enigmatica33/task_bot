from aiogram.fsm.state import State, StatesGroup


class MainMenu(StatesGroup):
    view_tasks = State()
    details = State()
    view_completed_tasks = State()


class AddTask(StatesGroup):
    select_category = State()
    input_title = State()
    success = State()
    input_description = State()
    input_due_date = State()
