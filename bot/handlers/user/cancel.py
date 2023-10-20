import logging

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from keyboards.reply import user_reply
from messages.user import cancel_message


async def handle_cancel(message: types.Message, state: FSMContext) -> None:
    """Хендлер сообщения об отмене действия."""
    logging.info(await state.get_state())
    logging.info(await state.get_data())
    await state.reset_state()
    await state.reset_data()
    await message.answer(cancel_message.cancel_message(),
                         reply_markup=user_reply.bot_main_keyboard())


def register_cancel_handler(dp: Dispatcher) -> None:
    dp.register_message_handler(handle_cancel, text='Отменить 🛑', state='*')
