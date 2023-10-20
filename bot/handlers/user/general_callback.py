from aiogram import Dispatcher
from aiogram.types import CallbackQuery
from messages.user import general_messages as general_msg


async def general_callback_handler(query: CallbackQuery):
    """Хендлер callbacks, которые не попали ни в один из зарегестрированных ранее."""
    if query.message.reply_markup:
        await query.message.edit_text(text=general_msg.inline_not_available(), reply_markup=None)


def register_general_callback_handler(dp: Dispatcher) -> None:
    """Регистрация хендлера general callbacks."""
    dp.register_callback_query_handler(
        general_callback_handler,
        state='*'
    )
