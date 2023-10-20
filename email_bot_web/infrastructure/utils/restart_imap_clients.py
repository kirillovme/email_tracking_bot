import asyncio

from django.conf import settings
from email_service.repositories import (
    BoxFilterRepository,
    EmailBoxRepository,
    EmailDomainRepository,
)
from infrastructure.gateways.imap_client import IMAPClient, IMAPStatuses
from infrastructure.utils.encryption_service import CryptoService
from user.repositories import BotUserRepository


async def restart_imap_clients() -> None:
    """Асинхронный перезапуск всех активных почтовых ящиков у активных пользователей."""
    crypto_service = CryptoService(settings.CRYPTO_KEY)
    active_users = await BotUserRepository.get_active_users()
    for user in active_users:
        active_email_boxes = await EmailBoxRepository.get_user_boxes(user.telegram_id)
        for box in active_email_boxes:
            email_service = await EmailDomainRepository.get_service(box.email_service_id)
            box_filters = await BoxFilterRepository.get_filters(box.id)
            whitelist = {filter_obj.filter_value for filter_obj in box_filters}
            await asyncio.sleep(5)
            imap_client = IMAPClient(
                host=email_service.address,
                user=box.email_username,
                password=crypto_service.decrypt_password(box.email_password),
                telegram_id=user.telegram_id,
                box_id=box.id,
                whitelist=whitelist
            )
            if box.is_active:
                asyncio.create_task(imap_client.imap_loop())
            else:
                asyncio.create_task(imap_client.imap_loop(initial_state=IMAPStatuses.PAUSED.value))
