from aiogram import Dispatcher, types
from messages.user import general_messages as general_mg


async def handle_general_messages(message: types.Message) -> None:
    """Хендлер сообщений, который не попали в остальные хендлеры."""
    await message.answer(text=general_mg.no_context_messages())


def register_general_messages_handler(dp: Dispatcher) -> None:
    """Регистрация хендлера не пойманных сообщений."""
    dp.register_message_handler(handle_general_messages, state='*')
