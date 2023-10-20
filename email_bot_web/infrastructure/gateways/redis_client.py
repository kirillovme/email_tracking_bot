import functools
from typing import Any, Callable

from django.conf import settings
from django.core.cache import cache
from django_redis import get_redis_connection


class RedisClient:
    """Класс для синхронного и асинхронного взаимодействия с Redis."""

    def __init__(self):
        self.client = get_redis_connection('default')

    def _make_key(self, key: str | bytes) -> str:
        """Получить ключ с указанием версии."""
        return cache.make_key(key)

    async def get(self, key: str | bytes) -> str | None:
        """Асинхронное получение значения по ключу."""
        return await cache.aget(key)

    async def set(self, key: str | bytes, value: str | bytes, timeout: int | None = None) -> None:
        """Асинхронное добавление ключа и значения в Redis."""
        await cache.aset(key, value, timeout=timeout)

    async def delete(self, key: str | bytes) -> int:
        """Асинхронное удаление ключа из Redis."""
        return await cache.adelete(key)

    async def exists(self, key) -> int:
        """Асинхронная проверка наличия ключа в Redis."""
        return await cache.ahas_key(key)

    async def get_all_telegram_ids(self) -> list[str]:
        """Асинхронное получение всех telegram_id из Redis."""
        cursor = '0'
        telegram_ids = set()

        while cursor != 0:
            cursor, keys = await self.client.scan(cursor=cursor, match='telegram_id_*_emails')
            for key in keys:
                telegram_id = key.decode('utf-8').split('_')[2]
                telegram_ids.add(telegram_id)

        return list(telegram_ids)

    def set_sync(self, key: str | bytes, value: str | bytes, timeout: int | None = None):
        """Синхронное добавление ключа и значения в Redis."""
        return cache.set(key, value, timeout=timeout)

    def exists_sync(self, key: str | bytes) -> bool:
        """Синхронная проверка наличия ключа в Redis."""
        return cache.has_key(key)

    def prepend_to_list(self, key: str | bytes, value: str | bytes) -> int:
        """Синхронное добавление значения в начало списка по ключу."""
        versioned_key = self._make_key(key)
        return self.client.lpush(versioned_key, value)

    def get_all_keys(self, pattern: str = '*') -> list[bytes]:
        """Синхронное получение всех ключей из Redis по заданному шаблону."""
        versioned_key = self._make_key(pattern)
        return self.client.keys(versioned_key)

    def remove_from_list(self, key: str | bytes, value: str | bytes) -> int:
        """Синхронное удаление указанного значения из списка по ключу."""
        versioned_key = self._make_key(key)
        return self.client.lrem(versioned_key, 1, value)

    def get_list_all_items(self, key: str | bytes) -> list[bytes]:
        """Синхронное получение всех элементов списка по ключу."""
        return self.client.lrange(key, 0, -1)

    def lpop(self, key: str | bytes) -> bytes | None:
        """Синхронное удаление и возврат первого элемента из списка по ключу."""
        return self.client.lpop(key)

    def touch(self, key: str | bytes, timeout: int | None = None) -> bool:
        """Синхроная установка времени жизни ключа."""
        return cache.touch(key, timeout)

    def cache_result(self, key_format: str, timeout: int = settings.CACHE_TIMEOUT) -> Callable:
        """Декоратор для кеширования результатов функции"""

        def decorator(func: Callable) -> Callable:

            @functools.wraps(func)
            async def wrapper(*args: Any, **kwargs: Any) -> Any:
                all_args = {**kwargs}
                for i, arg in enumerate(args):
                    all_args[func.__code__.co_varnames[i]] = arg
                cache_key = key_format.format(**all_args)
                cached_value = cache.get(cache_key)
                if cached_value is not None:
                    return cached_value
                result = await func(*args, **kwargs)
                cache.set(cache_key, result, timeout=timeout)
                return result

            return wrapper

        return decorator

    def invalidate_cache(self, key_format_list: list[str]) -> Callable:
        """Инвалидация кеша на основании полученных форматов ключей."""

        def decorator(func: Callable) -> Callable:

            @functools.wraps(func)
            async def wrapper(*args: Any, **kwargs: Any) -> Any:
                all_args = {**kwargs}
                for i, arg in enumerate(args):
                    all_args[func.__code__.co_varnames[i]] = arg
                for key_format in key_format_list:
                    cache_key = key_format.format(**all_args)
                    await cache.adelete(cache_key)
                result = await func(*args, **kwargs)
                return result

            return wrapper

        return decorator


redis_client = RedisClient()
