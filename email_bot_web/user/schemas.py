from ninja import ModelSchema
from user.models import BotUser


class BotUserIn(ModelSchema):
    """Схема для получения пользователя бота"""

    class Config:
        model = BotUser
        model_fields = ['telegram_id']
