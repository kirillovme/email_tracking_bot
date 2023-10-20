from django.conf import settings
from email_service.models import BoxFilter, EmailBox, EmailService
from email_service.schemas import BoxFilterSchema, EmailBoxIn
from infrastructure.gateways.redis_client import redis_client


class EmailDomainRepository:
    """Репозиторий для работы с моделью EmailService."""

    @staticmethod
    @redis_client.cache_result(key_format=settings.EMAIL_SERVICE_KEY_FORMAT)
    async def get_service(service_id: int) -> EmailService:
        """Асинхронно получает сервис электронной почты по его идентификатору."""
        service = await EmailService.objects.aget(id=service_id)
        return service

    @staticmethod
    @redis_client.cache_result(key_format=settings.EMAIL_SERVICES_KEY_FORMAT)
    async def get_services() -> list[EmailService]:
        """Асинхронно получает список всех сервисов электронной почты."""
        return [service async for service in EmailService.objects.all()]


class BoxFilterRepository:
    """Репозиторий для работы с моделью BoxFilter."""

    @staticmethod
    @redis_client.invalidate_cache(key_format_list=[settings.BOX_FILTERS_KEY_FORMAT])
    async def create_filters(box_id: int, box_filters_data: list[BoxFilterSchema]) -> list[BoxFilter]:
        """Асинхронно создает фильтры для указанного ящика."""
        box_filters_to_add = [BoxFilter(
            box_id=box_id,
            filter_value=box_filter.filter_value,
            filter_name=box_filter.filter_name
        ) for box_filter in box_filters_data]
        return await BoxFilter.objects.abulk_create(box_filters_to_add)

    @staticmethod
    @redis_client.cache_result(key_format=settings.BOX_FILTERS_KEY_FORMAT)
    async def get_filters(box_id: int) -> list[BoxFilter]:
        """Асинхронно получает фильтры для указанного ящика."""
        return [box_filter async for box_filter in BoxFilter.objects.filter(box_id=box_id)]


class EmailBoxRepository:
    """Репозиторий для работы с моделью EmailBox."""

    @staticmethod
    @redis_client.invalidate_cache(key_format_list=[settings.USER_EMAIL_BOXES_KEY_FORMAT])
    async def create_box(
            telegram_id: int,
            email_domain_id: int,
            payload: EmailBoxIn
    ) -> EmailBox:
        """Асинхронно создает почтовый ящик."""
        email_box = await EmailBox.objects.acreate(
            user_id=telegram_id,
            email_service=email_domain_id,
            email_username=payload.email_username,
            email_password=payload.email_password
        )
        return email_box

    @staticmethod
    @redis_client.cache_result(key_format=settings.EMAIL_BOX_KEY_FORMAT)
    async def get_box(box_id: int) -> EmailBox:
        """Асинхронно получает почтовый ящик по его идентификатору."""
        return await EmailBox.objects.aget(id=box_id)

    @staticmethod
    @redis_client.invalidate_cache(
        key_format_list=[
            settings.USER_EMAIL_BOXES_KEY_FORMAT,
            settings.EMAIL_BOX_KEY_FORMAT
        ]
    )
    async def delete_box(box_id: int, telegram_id: int) -> None:
        """Асинхронно удаляет почтовый ящик."""
        await EmailBox.objects.filter(id=box_id).adelete()

    @staticmethod
    @redis_client.cache_result(key_format=settings.USER_EMAIL_BOXES_KEY_FORMAT)
    async def get_user_boxes(telegram_id: int) -> list[EmailBox]:
        """Асинхронно получает список всех ящиков, принадлежащих пользователю с указанным telegram_id."""
        return [email_box async for email_box in EmailBox.objects.filter(user_id=telegram_id)]

    @staticmethod
    @redis_client.invalidate_cache(
        key_format_list=[
            settings.USER_EMAIL_BOXES_KEY_FORMAT,
            settings.EMAIL_BOX_KEY_FORMAT
        ]
    )
    async def pause_box_listening(box_id: int, telegram_id: int) -> None:
        """Асинхронно ставит на паузу прослушивание почтового ящика (устанавливает is_active в False)."""
        await EmailBox.objects.filter(id=box_id).aupdate(is_active=False)

    @staticmethod
    @redis_client.invalidate_cache(
        key_format_list=[
            settings.USER_EMAIL_BOXES_KEY_FORMAT,
            settings.EMAIL_BOX_KEY_FORMAT
        ]
    )
    async def resume_box_listening(box_id: int, telegram_id: int) -> None:
        """Асинхронно возобновляет прослушивание почтового ящика (устанавливает is_active в True)."""
        await EmailBox.objects.filter(id=box_id).aupdate(is_active=True)
