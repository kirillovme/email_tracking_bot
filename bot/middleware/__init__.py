from aiogram import Dispatcher

from .api_middleware import ApiMiddleware
from .throttling_middleware import ThrottlingMiddleware


def register_middlewares(dp: Dispatcher) -> None:
    """Регистрация всех middlewares."""
    dp.setup_middleware(ApiMiddleware())
    dp.setup_middleware(ThrottlingMiddleware())
