import asyncio

from django.conf import settings
from django.db import IntegrityError
from email_service.models import BoxFilter, EmailBox, EmailService
from email_service.schemas import EmailBoxIn
from infrastructure.exceptions import (
    AppliedFiltersNotFound,
    AvailableServicesNotFound,
    BotUserNotFound,
    BoxUserNotEqualToRequestedTelegramUser,
    EmailBoxAlreadyExists,
    EmailBoxNotFound,
    EmailCredsInvalid,
    EmailServiceNotFound,
    UserBoxesNotFound,
)
from infrastructure.gateways.imap_client import (
    IMAPClient,
    IMAPConnectionManager,
    IMAPStatuses,
)
from infrastructure.gateways.redis_client import redis_client
from infrastructure.repositories import EmailBotWebRepository
from infrastructure.utils.encryption_service import CryptoService
from user.models import BotUser


class EmailDomainService:
    """Сервисный слой для модели EmailService."""

    def __init__(self):
        self.repo = EmailBotWebRepository()

    async def get_services(self) -> list[EmailService]:
        """Асинхронное получение списка сервисов и обработка ошибок."""
        if services := await self.repo.email_domain_repo.get_services():
            return services
        else:
            raise AvailableServicesNotFound


class EmailBoxService:
    """Сервисный слой для модели EmailBox."""

    def __init__(self):
        self.repo = EmailBotWebRepository()

    async def create_box(self, telegram_id: int, payload: EmailBoxIn) -> EmailBox:
        """Асинхронное создание почты и обработка ошибок."""
        try:
            crypto_service = CryptoService(settings.CRYPTO_KEY)
            bot_user = await self.repo.bot_user_repo.get_user(telegram_id)
            email_service = await self.repo.email_domain_repo.get_service(payload.email_service)
            imap_connection_manager = IMAPConnectionManager(
                email_service.address,
                payload.email_username,
                crypto_service.decrypt_password(payload.email_password)
            )
            if not await imap_connection_manager.check_connection():
                raise EmailCredsInvalid
            email_box = await self.repo.email_box_repo.create_box(bot_user, email_service, payload)
            box_filters = await self.repo.box_filter_repo.create_filters(email_box, payload.filters)
            whitelist = {filter_obj.filter_value for filter_obj in box_filters}
            imap_client = IMAPClient(
                host=email_service.address,
                user=email_box.email_username,
                password=crypto_service.decrypt_password(email_box.email_password),
                telegram_id=telegram_id,
                box_id=email_box.id,
                whitelist=whitelist
            )
            asyncio.create_task(imap_client.imap_loop())
            return email_box
        except BotUser.DoesNotExist:
            raise BotUserNotFound
        except EmailService.DoesNotExist:
            raise EmailServiceNotFound
        except IntegrityError:
            raise EmailBoxAlreadyExists

    async def get_box_with_filters(self, telegram_id: int, box_id: int) -> tuple[EmailBox, list[BoxFilter]]:
        """Асинхронное получение почтового ящика c фильтрами и обработка ошибок."""
        try:
            bot_user = await self.repo.bot_user_repo.get_user(telegram_id)
            email_box = await self.repo.email_box_repo.get_box(box_id)
            box_filters = await self.repo.box_filter_repo.get_filters(box_id)
        except BotUser.DoesNotExist:
            raise BotUserNotFound
        except EmailBox.DoesNotExist:
            raise EmailBoxNotFound
        if not (email_box.user_id_id == bot_user.telegram_id):
            raise BoxUserNotEqualToRequestedTelegramUser
        return email_box, box_filters

    async def get_user_boxes(self, telegram_id: int) -> list[EmailBox]:
        """Асинхронное получения почтовых ящиков пользователя и обработка ошибок."""
        try:
            await self.repo.bot_user_repo.get_user(telegram_id)
            if user_boxes := await self.repo.email_box_repo.get_user_boxes(telegram_id=telegram_id):
                return user_boxes
            else:
                raise UserBoxesNotFound
        except BotUser.DoesNotExist:
            raise BotUserNotFound

    async def delete_box(self, telegram_id: int, box_id: int) -> None:
        """Асинхронное удаление почтового ящика и обработка ошибок."""
        try:
            bot_user = await self.repo.bot_user_repo.get_user(telegram_id)
            email_box = await self.repo.email_box_repo.get_box(box_id)
            if not (email_box.user_id_id == bot_user.telegram_id):
                raise BoxUserNotEqualToRequestedTelegramUser
            await self.repo.email_box_repo.delete_box(box_id, telegram_id)
            await redis_client.set(f'imap_client_status_{telegram_id}_{box_id}', IMAPStatuses.STOPPED.value)
        except BotUser.DoesNotExist:
            raise BotUserNotFound
        except EmailBox.DoesNotExist:
            raise EmailBoxNotFound

    async def pause_box_listening(self, telegram_id: int, box_id: int) -> None:
        """Асинхронная остановка прослушивания почты и обработка ошибок."""
        try:
            bot_user = await self.repo.bot_user_repo.get_user(telegram_id)
            email_box = await self.repo.email_box_repo.get_box(box_id)
            if not (email_box.user_id_id == bot_user.telegram_id):
                raise BoxUserNotEqualToRequestedTelegramUser
            await self.repo.email_box_repo.pause_box_listening(box_id, telegram_id)
            cache_key = settings.IMAP_CLIENT_STATUS_KEY_FORMAT.format(
                telegram_id=telegram_id,
                box_id=box_id
            )
            await redis_client.set(cache_key, IMAPStatuses.PAUSED.value)
        except EmailBox.DoesNotExist:
            raise EmailBoxNotFound
        except BotUser.DoesNotExist:
            raise BotUserNotFound

    async def resume_box_listening(self, telegram_id: int, box_id: int) -> None:
        """Асинхронное возобновление прослушивания почты и обработка ошибок."""
        try:
            bot_user = await self.repo.bot_user_repo.get_user(telegram_id)
            email_box = await self.repo.email_box_repo.get_box(box_id)
            if not (email_box.user_id_id == bot_user.telegram_id):
                raise BoxUserNotEqualToRequestedTelegramUser
            await self.repo.email_box_repo.resume_box_listening(box_id, telegram_id)
            cache_key = settings.IMAP_CLIENT_STATUS_KEY_FORMAT.format(
                telegram_id=telegram_id,
                box_id=box_id
            )
            await redis_client.set(cache_key, IMAPStatuses.ACTIVE.value)
        except EmailBox.DoesNotExist:
            raise EmailBoxNotFound
        except BotUser.DoesNotExist:
            raise BotUserNotFound


class BoxFilterService:
    """Сервисный слой для модели BoxFilter."""

    def __init__(self):
        self.repo = EmailBotWebRepository()

    async def get_filters(self, telegram_id: int, box_id: int) -> list[BoxFilter]:
        """Асинхронное получение списка фильтров и обработка ошибок."""
        try:
            bot_user = await self.repo.bot_user_repo.get_user(telegram_id)
            email_box = await self.repo.email_box_repo.get_box(box_id)
        except BotUser.DoesNotExist:
            raise BotUserNotFound
        except EmailBox.DoesNotExist:
            raise EmailBoxNotFound
        if not (email_box.user_id_id == bot_user.telegram_id):
            raise BoxUserNotEqualToRequestedTelegramUser
        if box_filters := await self.repo.box_filter_repo.get_filters(box_id):
            return box_filters
        else:
            raise AppliedFiltersNotFound
