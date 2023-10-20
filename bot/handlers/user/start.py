import html

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from config.config import API_ERROR
from keyboards.reply import user_reply
from messages.user import start_message
from utils.api_client import APIClient


async def handle_start_command(message: types.Message, state: FSMContext, api: APIClient) -> None:
    """Хендлер команды /start."""
    await state.reset_state()
    await state.reset_data()
    user_id = message.from_user.id
    exists_response = await api.user_exists(telegram_id=user_id)
    if exists_response.error:
        create_response = await api.create_user(telegram_id=user_id)
        if create_response.error:
            await message.answer(API_ERROR)
            return
    await message.answer(start_message.welcome_user(html.escape(message.from_user.full_name)),
                         reply_markup=user_reply.bot_main_keyboard())


def register_start_handler(dp: Dispatcher) -> None:
    """Регистрация хенделера."""
    dp.register_message_handler(handle_start_command, commands=['start'], state='*')
