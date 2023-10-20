from http import HTTPStatus
from typing import Any

from api.v1.schemas import ResponseSchema
from django.http import HttpRequest
from email_service.schemas import EmailServicesList
from email_service.services import EmailDomainService
from infrastructure.exceptions import AvailableServicesNotFound
from ninja import Router

service_router = Router(tags=['Почтовые сервисы'])

email_domain_service = EmailDomainService()


@service_router.get(
    '',
    response={
        HTTPStatus.OK: EmailServicesList,
        HTTPStatus.NOT_FOUND: ResponseSchema
    },
    description='Получение списка всех доступных сервисов с поддержкой imap',
    summary='Получение спиcка сервисов'
)
async def get_services(request: HttpRequest) -> tuple[HTTPStatus, dict[str, Any]]:
    """Получение списка всех доступных сервисов с поддержкой IMAP."""
    try:
        email_services = await email_domain_service.get_services()
        return HTTPStatus.OK, {'services': email_services}
    except AvailableServicesNotFound:
        return HTTPStatus.NOT_FOUND, {'message': 'No available services found'}
