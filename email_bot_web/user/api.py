from http import HTTPStatus
from typing import Any

from api.v1.schemas import ResponseSchema
from django.http import HttpRequest
from email_service.schemas import (
    BoxFiltersOut,
    EmailBoxesOut,
    EmailBoxIn,
    EmailBoxWithFiltersOut,
)
from email_service.services import BoxFilterService, EmailBoxService
from infrastructure.exceptions import (
    AppliedFiltersNotFound,
    BotUserAlreadyExists,
    BotUserNotFound,
    BoxUserNotEqualToRequestedTelegramUser,
    EmailBoxAlreadyExists,
    EmailBoxNotFound,
    EmailCredsInvalid,
    EmailServiceNotFound,
    IMAPServerTimeout,
    UserBoxesNotFound,
)
from ninja import Router
from user.schemas import BotUserIn
from user.services import BotUserService

user_router = Router(tags=['Пользователи'])

bot_user_service = BotUserService()
email_box_service = EmailBoxService()
box_filter_service = BoxFilterService()


@user_router.post(
    '',
    response={
        HTTPStatus.CREATED: ResponseSchema,
        HTTPStatus.BAD_REQUEST: ResponseSchema
    },
    description='Создание нового пользователя с помощью /register',
    summary='Создание пользователя'
)
async def create_user(request: HttpRequest, payload: BotUserIn) -> tuple[HTTPStatus, dict[str, Any]]:
    """Создание нового пользователя."""
    try:
        await bot_user_service.create_user(payload.telegram_id)
        return HTTPStatus.CREATED, {'message': 'Bot user was successfully created'}
    except BotUserAlreadyExists:
        return HTTPStatus.BAD_REQUEST, {'message': 'Bot user already exists'}


@user_router.get(
    '/{telegram_id}/exists',
    response={
        HTTPStatus.OK: ResponseSchema,
        HTTPStatus.NOT_FOUND: ResponseSchema
    },
    description='Проверка существования пользователя',
    summary='Проверка существования пользователя'
)
async def user_exists(request: HttpRequest, telegram_id: int) -> tuple[HTTPStatus, dict[str, Any]]:
    """Проверка существования пользователя по его telegram_id."""
    if await bot_user_service.user_exists(telegram_id):
        return HTTPStatus.OK, {'message': f'Bot user with telegram_id:{telegram_id} exists'}
    else:
        return HTTPStatus.NOT_FOUND, {'message': f'Bot user with telegram_id:{telegram_id} doesn\'t exist'}


@user_router.post(
    '/{telegram_id}/boxes',
    response={
        HTTPStatus.CREATED: ResponseSchema,
        HTTPStatus.BAD_REQUEST: ResponseSchema,
        HTTPStatus.NOT_FOUND: ResponseSchema
    },
    description='Создание нового почтового ящика для пользователя с {telegram_id}',
    summary='Создание почтового ящика'
)
async def create_box(request: HttpRequest, telegram_id: int, payload: EmailBoxIn) -> tuple[HTTPStatus, dict[str, Any]]:
    """Создание нового почтового ящика для указанного пользователя."""
    try:
        await email_box_service.create_box(telegram_id=telegram_id, payload=payload)
        return HTTPStatus.CREATED, {'message': 'Email box successfully created'}
    except BotUserNotFound:
        return HTTPStatus.NOT_FOUND, {'message': f'Requested bot user with telegram_id:{telegram_id} doesn\'t exist'}
    except EmailServiceNotFound:
        return (
            HTTPStatus.NOT_FOUND,
            {'message': f'Requested email service with id:{payload.email_service} doesn\'t exist'}
        )
    except EmailBoxAlreadyExists:
        return HTTPStatus.BAD_REQUEST, {'message': 'This email box already exists'}
    except EmailCredsInvalid:
        return HTTPStatus.BAD_REQUEST, {'message': 'Your email credentials are incorrect'}
    except IMAPServerTimeout:
        return HTTPStatus.BAD_REQUEST, {'message': 'IMAP server is not responding'}


@user_router.get(
    '/{telegram_id}/boxes',
    response={
        HTTPStatus.OK: EmailBoxesOut,
        HTTPStatus.NOT_FOUND: ResponseSchema
    },
    description='Получение списка почтовых ящиков для пользователя с {telegram_id}',
    summary='Получение списка почтовых ящиков'
)
async def get_user_boxes(request: HttpRequest, telegram_id: int) -> tuple[HTTPStatus, dict[str, Any]]:
    """Получение списка почтовых ящиков для указанного пользователя."""
    try:
        user_boxes = await email_box_service.get_user_boxes(telegram_id=telegram_id)
        return HTTPStatus.OK, {'email_boxes': user_boxes}
    except UserBoxesNotFound:
        return HTTPStatus.NOT_FOUND, {'message': 'You do not have any email boxes yet'}
    except BotUserNotFound:
        return HTTPStatus.NOT_FOUND, {'message': f'Requested bot user with telegram_id:{telegram_id} doesn\'t exist'}


@user_router.get(
    '{telegram_id}/boxes/{box_id}',
    response={
        HTTPStatus.OK: EmailBoxWithFiltersOut,
        HTTPStatus.NOT_FOUND: ResponseSchema
    },
    description='Получение почтового ящика {box_id} пользователя {telegram_id}',
    summary='Получение почтового ящика'
)
async def get_box(
        request: HttpRequest,
        telegram_id: int,
        box_id: int
) -> tuple[HTTPStatus, dict[str, Any]]:
    """Получение почтового ящика."""
    try:
        email_box, box_filters = await email_box_service.get_box_with_filters(telegram_id=telegram_id, box_id=box_id)
        return HTTPStatus.OK, {
            'id': email_box.id,
            'email_service_id': email_box.email_service_id,
            'email_username': email_box.email_username,
            'is_active': email_box.is_active,
            'filters': box_filters
        }
    except BotUserNotFound:
        return HTTPStatus.NOT_FOUND, {'message': f'Requested bot user with telegram_id:{telegram_id} doesn\'t exist'}
    except EmailBoxNotFound:
        return HTTPStatus.NOT_FOUND, {'message': f'Requsted email box with id:{box_id} not found'}
    except BoxUserNotEqualToRequestedTelegramUser:
        return HTTPStatus.BAD_REQUEST, {'message': 'Requested bot user doesn\'t have this email box'}


@user_router.delete(
    '{telegram_id}/boxes/{box_id}',
    response={
        HTTPStatus.NO_CONTENT: None,
        HTTPStatus.BAD_REQUEST: ResponseSchema,
        HTTPStatus.NOT_FOUND: ResponseSchema
    },
    description='Удаление почтового ящика {box_id} пользователя {telegram_id}',
    summary='Удаление почтового ящика'
)
async def delete_box(
        request: HttpRequest,
        telegram_id: int,
        box_id: int
) -> tuple[HTTPStatus, dict[str, Any]]:
    """Удаление почтового ящика пользователя."""
    try:
        await email_box_service.delete_box(telegram_id=telegram_id, box_id=box_id)
        return HTTPStatus.NO_CONTENT, {}
    except BotUserNotFound:
        return HTTPStatus.NOT_FOUND, {'message': f'Requested bot user with telegram_id:{telegram_id} doesn\'t exist'}
    except EmailBoxNotFound:
        return HTTPStatus.NOT_FOUND, {'message': f'Requsted email box with id:{box_id} not found'}
    except BoxUserNotEqualToRequestedTelegramUser:
        return HTTPStatus.BAD_REQUEST, {'message': 'Requested bot user doesn\'t have this email box'}


@user_router.get(
    '/{telegram_id}/boxes/{box_id}/filters',
    response={
        HTTPStatus.OK: BoxFiltersOut,
        HTTPStatus.NOT_FOUND: ResponseSchema,
        HTTPStatus.BAD_REQUEST: ResponseSchema
    },
    description='Поучение фильтров, примененных пользователем {telegram_id} к почтовому ящику {box_id}',
    summary='Получение всех фильтров, примененных к почтовому ящику'
)
async def get_filters(request: HttpRequest, telegram_id: int, box_id: int) -> tuple[HTTPStatus, dict[str, Any]]:
    """Получение фильтров, примененных к почтовому ящику."""
    try:
        box_filters = await box_filter_service.get_filters(telegram_id, box_id)
        return HTTPStatus.OK, {'filters': box_filters}
    except AppliedFiltersNotFound:
        return HTTPStatus.NOT_FOUND, {'message': f'There are no applied filters for the email box with id:{box_id}'}
    except BotUserNotFound:
        return HTTPStatus.NOT_FOUND, {'message': f'Requested bot user with telegram_id:{telegram_id} doesn\'t exist'}
    except EmailBoxNotFound:
        return HTTPStatus.NOT_FOUND, {'message': f'Requsted email box with id:{box_id} not found'}
    except BoxUserNotEqualToRequestedTelegramUser:
        return HTTPStatus.BAD_REQUEST, {'message': 'Requested bot user doesn\'t have this email box'}


@user_router.get(
    '/{telegram_id}/boxes/{box_id}/pause',
    response={
        HTTPStatus.OK: ResponseSchema,
        HTTPStatus.NOT_FOUND: ResponseSchema,
        HTTPStatus.BAD_REQUEST: ResponseSchema
    },
    description='Остановка прослушивания новой почты пользователя {telegram_id}, почтового ящика {box_id}',
    summary='Остановка прослушивания почты отдельного почтового ящика'
)
async def pause_box_listening(request: HttpRequest, telegram_id: int, box_id: int) -> tuple[HTTPStatus, dict[str, Any]]:
    """Остановка прослушивания почты отдельного почтового ящика."""
    try:
        await email_box_service.pause_box_listening(telegram_id=telegram_id, box_id=box_id)
        return HTTPStatus.OK, {'message': f'The user:{telegram_id} box:{box_id} listening was paused'}
    except EmailBoxNotFound:
        return HTTPStatus.NOT_FOUND, {'message': f'Requsted email box with id:{box_id} not found'}
    except BoxUserNotEqualToRequestedTelegramUser:
        return HTTPStatus.BAD_REQUEST, {'message': 'Requested bot user doesn\'t have this email box'}


@user_router.get(
    '/{telegram_id}/boxes/{box_id}/resume',
    response={
        HTTPStatus.OK: ResponseSchema,
        HTTPStatus.NOT_FOUND: ResponseSchema,
        HTTPStatus.BAD_REQUEST: ResponseSchema
    },
    description='Возобновление прослушивания новой почты пользователя {telegram_id}, почтового ящика {box_id}',
    summary='Возобновление прослушивания почты отдельного почтового ящика'
)
async def resume_box_listening(
        request: HttpRequest,
        telegram_id: int,
        box_id: int
) -> tuple[HTTPStatus, dict[str, Any]]:
    """Возобновление прослушивания почты отдельного почтового ящика."""
    try:
        await email_box_service.resume_box_listening(telegram_id=telegram_id, box_id=box_id)
        return HTTPStatus.OK, {'message': f'The user:{telegram_id} box:{box_id} listening was resumed'}
    except EmailBoxNotFound:
        return HTTPStatus.NOT_FOUND, {'message': f'Requsted email box with id:{box_id} not found'}
    except BoxUserNotEqualToRequestedTelegramUser:
        return HTTPStatus.BAD_REQUEST, {'message': 'Requested bot user doesn\'t have this email box'}
