import logging
from http import HTTPStatus
from typing import Any

from aiogram.dispatcher.handler import CancelHandler
from config.config import (
    CREATE_BOX_ENDPOINT,
    CREATE_USER_ENDPOINT,
    DELETE_BOX_ENDPOINT,
    DOMAIN_LIST_ENDPOINT,
    GET_BOX_ENDPOINT,
    GET_BOXES_ENDPOINT,
    PAUSE_BOX_ENDPOINT,
    RESUME_BOX_ENDPOINT,
    USER_EXISTS_ENDPOINT,
)
from httpx import AsyncClient, ConnectError, Response, TimeoutException
from utils.exceptions import (
    APIInternalError,
    AvailableServicesNotFound,
    BotUserNotFound,
    EmailBoxNotFound,
    EmailCredsInvalid,
    UserBoxesNotFound,
)
from utils.schemas import APIResponse


class APIClient:
    """Клиент для взаимодействия с API"""

    def __init__(self, api_url: str):
        self.api_url = api_url
        self.client = AsyncClient()

    async def request(self, method: str, endpoint: str, data: dict[str, Any] | None = None) -> Response:
        """Общий метод для создания реквестов."""
        url = f'{self.api_url}/{endpoint}'
        try:
            response = await self.client.request(method, url, json=data)
            return response
        except (TimeoutException, ConnectError) as error:
            logging.error(f'API ERROR: {type(error)}. messsage: {error}')
            raise CancelHandler()

    async def user_exists(self, telegram_id: int) -> APIResponse:
        """GET запрос на существование пользователя."""
        response = await self.request('GET', USER_EXISTS_ENDPOINT.format(telegram_id=telegram_id))
        if response.status_code == HTTPStatus.OK:
            return APIResponse(data=True, error=None)
        elif response.status_code == HTTPStatus.NOT_FOUND:
            return APIResponse(data=None, error=BotUserNotFound)
        else:
            return APIResponse(data=None, error=APIInternalError)

    async def create_user(self, telegram_id: int) -> APIResponse:
        """POST запрос на создание пользователя."""
        data = {
            'telegram_id': telegram_id
        }
        response = await self.request('POST', CREATE_USER_ENDPOINT, data=data)
        if response.status_code == HTTPStatus.CREATED:
            return APIResponse(data=True, error=None)
        else:
            return APIResponse(data=None, error=APIInternalError)

    async def create_box(self, telegram_id: int, state_data: dict[str, Any]) -> APIResponse:
        """POST запрос на создание почтового ящика."""
        data = {
            'email_service_id': int(state_data['service']),
            'email_username': state_data['email_address'],
            'email_password': state_data['password'],
            'filters': state_data.get('filters', [])
        }
        response = await self.request('POST', CREATE_BOX_ENDPOINT.format(telegram_id=telegram_id), data=data)
        if response.status_code == HTTPStatus.CREATED:
            return APIResponse(data=True, error=None)
        elif response.status_code == HTTPStatus.BAD_REQUEST:
            return APIResponse(data=None, error=EmailCredsInvalid)
        else:
            return APIResponse(data=None, error=APIInternalError)

    async def get_services(self) -> APIResponse:
        """GET запрос на получение доступных сервисов."""
        response = await self.request('GET', DOMAIN_LIST_ENDPOINT)
        if response.status_code == HTTPStatus.OK:
            return APIResponse(data=response.json().get('services', []), error=None)
        elif response.status_code == HTTPStatus.NOT_FOUND:
            return APIResponse(data=None, error=AvailableServicesNotFound)
        else:
            return APIResponse(data=None, error=APIInternalError)

    async def get_user_boxes(self, telegram_id: int) -> APIResponse:
        """GET запрос на получение отслеживаемых почтовых ящиков."""
        response = await self.request('GET', GET_BOXES_ENDPOINT.format(telegram_id=telegram_id))
        if response.status_code == HTTPStatus.OK:
            return APIResponse(data=response.json().get('email_boxes', []), error=None)
        elif response.status_code == HTTPStatus.NOT_FOUND:
            return APIResponse(data=None, error=UserBoxesNotFound)
        else:
            return APIResponse(data=None, error=APIInternalError)

    async def get_user_box(self, telegram_id: int, box_id: int) -> APIResponse:
        """GET запрос на получение отдельного почтового ящика."""
        response = await self.request('GET', GET_BOX_ENDPOINT.format(telegram_id=telegram_id, box_id=box_id))
        if response.status_code == HTTPStatus.OK:
            return APIResponse(data=response.json(), error=None)
        elif response.status_code == HTTPStatus.NOT_FOUND:
            return APIResponse(data=None, error=EmailBoxNotFound)
        else:
            return APIResponse(data=None, error=APIInternalError)

    async def pause_box(self, telegram_id: int, box_id: int) -> APIResponse:
        """GET запрос на остановку отслеживания новых писем у почтового ящика."""
        response = await self.request('GET', PAUSE_BOX_ENDPOINT.format(telegram_id=telegram_id, box_id=box_id))
        if response.status_code == HTTPStatus.OK:
            return APIResponse(data=True, error=None)
        elif response.status_code == HTTPStatus.NOT_FOUND:
            return APIResponse(data=None, error=EmailBoxNotFound)
        else:
            return APIResponse(data=None, error=APIInternalError)

    async def resume_box(self, telegram_id: int, box_id: int) -> APIResponse:
        """GET запрос на возобновление отслеживания новых писем у почтового ящика."""
        response = await self.request('GET', RESUME_BOX_ENDPOINT.format(telegram_id=telegram_id, box_id=box_id))
        if response.status_code == HTTPStatus.OK:
            return APIResponse(data=True, error=None)
        elif response.status_code == HTTPStatus.NOT_FOUND:
            return APIResponse(data=None, error=EmailBoxNotFound)
        else:
            return APIResponse(data=None, error=APIInternalError)

    async def delete_box(self, telegram_id: int, box_id: int) -> APIResponse:
        """DELETE запрос на удаление почтового ящика."""
        response = await self.request('DELETE', DELETE_BOX_ENDPOINT.format(telegram_id=telegram_id, box_id=box_id))
        if response.status_code == HTTPStatus.NO_CONTENT:
            return APIResponse(data=True, error=None)
        elif response.status_code == HTTPStatus.NOT_FOUND:
            return APIResponse(data=None, error=EmailBoxNotFound)
        else:
            return APIResponse(data=None, error=APIInternalError)

    async def close(self) -> None:
        """Отсоединение клиента."""
        await self.client.aclose()
