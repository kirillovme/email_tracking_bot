from aiogram import Dispatcher

from .start import register_start_handler
from .add_box import register_add_email_handler
from .get_boxes import register_my_boxes_handler
from .cancel import register_cancel_handler
from .general_callback import register_general_callback_handler
from .general_messages import register_general_messages_handler


def register_user_handlers(dp: Dispatcher):
    """Регистрация всех хендлеров для взаимодействия с пользователем."""
    register_start_handler(dp)
    register_cancel_handler(dp)
    register_add_email_handler(dp)
    register_my_boxes_handler(dp)
    register_general_callback_handler(dp)
    register_general_messages_handler(dp)
