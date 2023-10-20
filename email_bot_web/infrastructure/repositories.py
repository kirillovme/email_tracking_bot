from email_service.repositories import (
    BoxFilterRepository,
    EmailBoxRepository,
    EmailDomainRepository,
)
from user.repositories import BotUserRepository


class EmailBotWebRepository:
    """Единый репозиторий для всех моделей."""

    def __init__(self):
        self.bot_user_repo = BotUserRepository
        self.email_domain_repo = EmailDomainRepository
        self.box_filter_repo = BoxFilterRepository
        self.email_box_repo = EmailBoxRepository
