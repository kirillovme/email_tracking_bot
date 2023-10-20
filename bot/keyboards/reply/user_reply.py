from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def bot_main_keyboard() -> ReplyKeyboardMarkup:
    """Главная клавиатура бота."""
    result_kb: ReplyKeyboardMarkup = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton('Добавить почтовый ящик 📧')],
        [KeyboardButton('Мои почтовые ящики 🗃')]
    ])
    return result_kb


def cancel_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для отмены текущего действия."""
    cancel_kb: ReplyKeyboardMarkup = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton('Отменить 🛑')]
    ])
    return cancel_kb
