from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def search_engines_keyboard(services: list) -> InlineKeyboardMarkup:
    """Клавиатура для выбора почтового сервиса."""
    engines_kb = InlineKeyboardMarkup()
    for service in services:
        engines_kb.add(InlineKeyboardButton(service['title'], callback_data=f'service:{service["id"]}'))
    return engines_kb


def more_filters_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора необходимости добавления дополнительных фильтров."""
    more_filters_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Да', callback_data='add_more_filters')],
        [InlineKeyboardButton('Нет', callback_data='no_more_filters')]
    ])
    return more_filters_kb
