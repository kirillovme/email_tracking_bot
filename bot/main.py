from aiogram import Dispatcher, executor
from handlers.user import register_user_handlers
from loader import dp
from middleware import register_middlewares


def regiter_handlers(dsp: Dispatcher) -> None:
    """Регистрация хендлеров."""
    register_user_handlers(dsp)


def regiter_middlewares(dsp: Dispatcher) -> None:
    """Регистрация мидлваров."""
    register_middlewares(dsp)


if __name__ == '__main__':
    regiter_handlers(dp)
    regiter_middlewares(dp)
    executor.start_polling(dp, skip_updates=True)
