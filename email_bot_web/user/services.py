from django.db import IntegrityError
from infrastructure.exceptions import BotUserAlreadyExists
from infrastructure.repositories import EmailBotWebRepository
from user.models import BotUser


class BotUserService:
    """Сервисный слой для модели BotUser"""

    def __init__(self):
        self.repo = EmailBotWebRepository()

    async def create_user(self, telegram_id: int) -> BotUser:
        """Асинхронное обращение к репозиторию и обработка ошибок при создании пользователя"""
        try:
            return await self.repo.bot_user_repo.create_user(telegram_id)
        except IntegrityError:
            raise BotUserAlreadyExists

    async def user_exists(self, telegram_id: int) -> bool:
        """Асинхронное обращение к репозиторию и обработка ошибок при проверке существования пользователя"""
        return await self.repo.bot_user_repo.user_exists(telegram_id)
