from django.conf import settings
from infrastructure.gateways.redis_client import redis_client
from user.models import BotUser


class BotUserRepository:
    """Репозиторий для модели BotUser."""

    @staticmethod
    @redis_client.invalidate_cache(
        key_format_list=[
            settings.BOT_USER_KEY_FORMAT,
            settings.ACTIVE_USERS_KEY_FORMAT,
            settings.USER_EXISTS_KEY_FORMAT
        ]
    )
    async def create_user(telegram_id: int) -> BotUser:
        """Асинхронное создание пользователя в базе данных с указанным telegram_id."""
        return await BotUser.objects.acreate(telegram_id=telegram_id)

    @staticmethod
    @redis_client.cache_result(key_format=settings.BOT_USER_KEY_FORMAT)
    async def get_user(telegram_id: int) -> BotUser:
        """Асинхронное получение пользователя из базы данных с указанным telegram_id."""
        return await BotUser.objects.aget(telegram_id=telegram_id)

    @staticmethod
    @redis_client.cache_result(key_format=settings.ACTIVE_USERS_KEY_FORMAT)
    async def get_active_users() -> list[BotUser]:
        """Асинхронное получение активных пользователей."""
        return [bot_user async for bot_user in BotUser.objects.filter(is_active=True)]

    @staticmethod
    @redis_client.cache_result(key_format=settings.USER_EXISTS_KEY_FORMAT)
    async def user_exists(telegram_id: int) -> bool:
        """Асинхронная проверка существования BotUser с указанным telegram_id в базе данных."""
        return await BotUser.objects.filter(telegram_id=telegram_id).aexists()
