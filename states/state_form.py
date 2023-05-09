from aiogram.dispatcher.filters.state import State, StatesGroup


class Form(StatesGroup):
    beginning = State()
    full_name = State()
    telefon = State()
    e_mail = State()
    firma = State()
    insert_in_base = State()
    description = State()
    priority = State()
    attach = State()
    end_form = State()
    send_request = State()
    add_for_firm = State()
    update_for_firm = State()