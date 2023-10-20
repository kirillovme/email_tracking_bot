from aiogram.dispatcher.filters.state import State, StatesGroup


class EmailBoxState(StatesGroup):
    """Класс состояний при добавлении почтового ящика."""
    service = State()
    email_address = State()
    password = State()
    filter_value = State()
    filter_name = State()
