from aiogram.fsm.state import StatesGroup, State


class CategoryState(StatesGroup):
    select_category = State()
    select_subcategory = State()


class AuthState(StatesGroup):
    start = State()
    set_login = State()
    set_password = State()
    set_phone = State()


class SchedulerState(StatesGroup):
    select_action = State()
    add_job_process_input = State()
    add_job = State()
    remove_job = State()


class BlacklistState(StatesGroup):
    manage = State()


class SettingsState(StatesGroup):
    edit = State()
