import os
from typing import Any, Awaitable, Callable

from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')


class LifespanApp:
    """Класс приложения ASGI для обработки событий жизненного цикла."""

    def __init__(self, app: Callable[[Any, Any, Any], Awaitable[None]]):
        """Инициализация LifespanApp с данным ASGI приложением."""
        self.app = app

    async def __call__(
            self,
            scope: dict,
            receive: Callable[[], Awaitable[dict]],
            send: Callable[[dict], Awaitable[None]]
    ) -> None:
        """Метод вызова для перенаправления запроса ASGI к обработчику жизненного цикла/приложению."""
        if scope['type'] == 'lifespan':
            await self.lifespan(scope, receive, send)
        else:
            await self.app(scope, receive, send)

    async def lifespan(
            self,
            scope: dict,
            receive: Callable[[], Awaitable[dict]],
            send: Callable[[dict], Awaitable[None]]
    ) -> None:
        """Обработка событий жизненного цикла."""
        message = await receive()
        if message['type'] == 'lifespan.startup':
            await self.startup()
            await send({'type': 'lifespan.startup.complete'})

    async def startup(self) -> None:
        """Обработчик события запуска жизненного цикла. Перезапускает клиенты IMAP."""
        from infrastructure.utils.restart_imap_clients import restart_imap_clients
        await restart_imap_clients()


django_asgi_app = ASGIStaticFilesHandler(get_asgi_application())
application = LifespanApp(django_asgi_app)
