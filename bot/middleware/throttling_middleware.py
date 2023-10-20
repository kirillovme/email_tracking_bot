import asyncio

from aiogram import Dispatcher, types
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Throttled


class ThrottlingMiddleware(BaseMiddleware):
    """Middleware для защиты от флуда."""

    DEFAULT_RATE_LIMIT = 1.0

    def __init__(self, limit=DEFAULT_RATE_LIMIT, key_prefix='antiflood_'):
        self.rate_limit = limit
        self.prefix = key_prefix
        super().__init__()

    async def on_process_message(self, message: types.Message, data: dict) -> None:
        """Вызывается для сообщений."""
        await self._throttle_handler(message, message.from_user.id)

    async def on_process_callback_query(self, query: types.CallbackQuery, data: dict) -> None:
        """Вызывается для callbacks."""
        await self._throttle_handler(query, query.from_user.id)

    async def _throttle_handler(self, obj, user_id) -> None:
        """Основная логика отловли ошибки Throttled, определения ключей и лимита."""
        handler = current_handler.get()
        dispatcher = Dispatcher.get_current()

        if handler:
            limit = getattr(handler, 'throttling_rate_limit', self.rate_limit)
            key = getattr(handler, 'throttling_key', f'{self.prefix}_{handler.__name__}_{user_id}')
        else:
            limit = self.rate_limit
            key = f'{self.prefix}_object_{user_id}'

        try:
            await dispatcher.throttle(key, rate=limit)
        except Throttled as t:
            await self._throttled_response(obj, t, key)
            raise CancelHandler()

    async def _throttled_response(self, obj, throttled: Throttled, key) -> None:
        """Логика ответа на ошибку Throttled."""
        delta = throttled.rate - throttled.delta

        if isinstance(obj, types.Message):
            reply_method = obj.reply
        elif isinstance(obj, types.CallbackQuery):
            def reply_method(text):
                return obj.answer(text, show_alert=True)

        if throttled.exceeded_count <= 2:
            await reply_method('Слишком много запросов! Будьте добры, помедленнее!')
        elif throttled.exceeded_count == 3:
            await reply_method(f'Слишком много запросов! Вы заблокированы на {delta:.0f} секунд.')

        await asyncio.sleep(delta)

        thr = await Dispatcher.get_current().check_key(key)
        if thr.exceeded_count == throttled.exceeded_count and isinstance(obj, types.CallbackQuery):
            await reply_method('Вы разблокированы. Можете продолжить работу с ботом.')
