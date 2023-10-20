import asyncio
import json
import logging
import re
from asyncio import wait_for
from collections import namedtuple
from email.header import decode_header
from email.message import Message
from email.parser import BytesHeaderParser, BytesParser
from enum import Enum
from functools import wraps
from typing import Any, Callable, Collection

import aioimaplib
from django.conf import settings
from email_service.tasks import email_html_to_image, send_image_to_telegram_task
from infrastructure.exceptions import (
    EmailCredsInvalid,
    IMAPClientIsNotConnected,
    IMAPServerTimeout,
)
from infrastructure.gateways.redis_client import redis_client
from infrastructure.utils.email_decoder import EmailDecoder

ID_HEADER_SET = {'Content-Type', 'From', 'To', 'Cc', 'Bcc', 'Date', 'Subject',
                 'Message-ID', 'In-Reply-To', 'References'}
FETCH_MESSAGE_DATA_UID = re.compile(rb'.*UID (?P<uid>\d+).*')
MessageAttributes = namedtuple('MessageAttributes', 'uid flags sequence_number')

logger = logging.getLogger('infrastructure')


def retry_async(max_retries: int = 5, delay_on_failure: int = 30) -> Callable:
    """Декоратор для асинхронных функций, который пытается повторно выполнить функцию при возникновении исключения."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            retries = 0
            while retries < max_retries:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    logger.error(f'Exception {type(e).__name__} occurred. Retry {retries}/{max_retries}.')
                    if retries < max_retries:
                        await asyncio.sleep(delay_on_failure)
            logger.error(f'Max retries reached for {func.__name__}. Exiting...')
            raise Exception(f'Max retries reached for {func.__name__}.')

        return wrapper

    return decorator


class IMAPConnectionManager:
    """Управление соединением и аутентификацией IMAP клиентов."""

    def __init__(self, host: str, user: str, password: str):
        self.host = host
        self.user = user
        self.password = password
        self.client = None

    async def check_connection(self) -> bool:
        """Проверка соединения с IMAP сервером."""
        try:
            test_client = aioimaplib.IMAP4_SSL(host=self.host, timeout=30)
            await test_client.wait_hello_from_server()
            response = await test_client.login(self.user, self.password)
        except asyncio.exceptions.TimeoutError:
            logger.error(f'The imap server {self.host} connection was timed out.')
            raise IMAPServerTimeout
        logger.info(f'The imap server {self.host} responded.')
        if response.result == IMAPStatuses.OK.value:
            logger.info(f'Test connection successfully worked for {self.user}. Logging out.')
            await test_client.logout()
            return True
        else:
            logger.error(f'Login credentials are wrong for {self.user}.')
            await test_client.logout()
            return False

    async def connect(self) -> None:
        """Соединение и аутентификация с IMAP сервером."""
        if not self.client:
            self.client = aioimaplib.IMAP4_SSL(host=self.host, timeout=30)
        try:
            await self.client.wait_hello_from_server()  # type: ignore
            response = await self.client.login(self.user, self.password)  # type: ignore
        except asyncio.exceptions.TimeoutError:
            logger.error(f'The imap server {self.host} connection was timed out.')
            raise IMAPServerTimeout
        if response.result == IMAPStatuses.OK.value:
            logger.info(f'User {self.user} successfully logged in.')
            await self.client.select('INBOX')  # type: ignore
        else:
            logger.error(f'Login credentials are wrong for {self.user}.')
            await self.client.logout()  # type: ignore
            raise EmailCredsInvalid

    def is_connected(self) -> bool:
        """Проверка наличия соединения с IMAP сервером."""
        if self.client:
            return self.client.has_pending_idle()
        return False

    async def disconnect(self) -> None:
        """Разрыв соединения с IMAP сервером."""
        if not self.client:
            raise IMAPClientIsNotConnected
        try:
            await self.client.logout()
        except asyncio.exceptions.TimeoutError:
            logger.error(f'Logout failed for user {self.user}. IMAP server - {self.host}')
            raise IMAPServerTimeout


class IMAPStatuses(Enum):
    """Статусы IMAP клиента."""

    ACTIVE = 'active'
    PAUSED = 'paused'
    STOPPED = 'stopped'
    OK = 'OK'


class RedisOperations:
    """Управление операциями с Redis для IMAP клиента."""

    def __init__(self, telegram_id: int, box_id: int):
        self.telegram_id = telegram_id
        self.box_id = box_id

    async def set_status(self, status: str) -> None:
        """Смена статуса IMAP клиента."""
        key = settings.IMAP_CLIENT_STATUS_KEY_FORMAT.format(
            telegram_id=self.telegram_id,
            box_id=self.box_id
        )
        await redis_client.set(key, status)

    async def get_status(self) -> str | None:
        """Получение статуса IMAP клиента."""
        key = settings.IMAP_CLIENT_STATUS_KEY_FORMAT.format(
            telegram_id=self.telegram_id,
            box_id=self.box_id
        )
        return await redis_client.get(key)

    async def remove_status(self) -> None:
        """Удаление статуса imap клиента."""
        key = settings.IMAP_CLIENT_STATUS_KEY_FORMAT.format(
            telegram_id=self.telegram_id,
            box_id=self.box_id
        )
        await redis_client.delete(key)

    async def prepend_email_to_list(self, decoded_email_params) -> None:
        """Присоеднение декодированных сообщений к списку с ключом telegram_id."""
        key = f'telegram_id_{self.telegram_id}_emails'
        logger.info(f'Prepended {decoded_email_params}')
        redis_client.prepend_to_list(key, json.dumps(decoded_email_params))


class IMAPClient:
    """Класс для работы с почтовыми сервисами по протоколу IMAP."""

    def __init__(self, host: str, user: str, password: str, telegram_id: int, box_id: int, whitelist: set):
        self.connection_manager = IMAPConnectionManager(host=host, user=user, password=password)
        self.redis_ops = RedisOperations(telegram_id=telegram_id, box_id=box_id)
        self.whitelist = set(whitelist) if whitelist else None
        self.persistent_max_uid = 1

    def extract_email(self, encoded_str: str) -> str | None:
        """Извлечение адреса электронной почты из строки."""
        decoded_list = decode_header(encoded_str)
        decoded_string = ''.join(
            [t[0].decode(t[1] or 'ascii') if isinstance(t[0], bytes) else t[0] for t in decoded_list])
        email_pattern = r'[\w\.-]+@[\w\.-]+'
        match = re.search(email_pattern, decoded_string)
        email_address = match.group(0) if match else None

        return email_address

    async def fetch_uid_from_seq_number(self, seq_number: str) -> int:
        """Получение UID по порядковому номеру."""
        if not self.connection_manager.client:
            raise IMAPClientIsNotConnected
        response = await self.connection_manager.client.fetch(seq_number, '(UID)')
        match_result = FETCH_MESSAGE_DATA_UID.match(response.lines[0])
        if match_result:
            return int(match_result.group('uid'))
        return 0

    async def fetch_messages_headers(self, uid: int) -> int:
        """Обработка сообщения с указанным UID и отправка письма пользователю."""
        if not self.connection_manager.client:
            raise IMAPClientIsNotConnected
        try:
            response = await self.connection_manager.client.uid('fetch', str(uid),
                                                                '(UID FLAGS BODY.PEEK[HEADER.FIELDS (%s)])' % ' '.join(
                                                                    ID_HEADER_SET))
        except asyncio.exceptions.TimeoutError:
            logger.error(
                f'Fetching headers failed for user {self.connection_manager.user}. IMAP server - {self.connection_manager.host}')
            raise IMAPServerTimeout
        if response.result == IMAPStatuses.OK.value:
            headers_line = response.lines[1]
            message_headers = BytesHeaderParser().parsebytes(headers_line)

            if not self.whitelist or (
                    self.whitelist and self.extract_email(message_headers.get('From')) in self.whitelist):
                body = await self.fetch_message_body(uid)
                raw_email_params = {
                    'Subject': message_headers.get('Subject'),
                    'From': message_headers.get('From'),
                    'To': message_headers.get('To'),
                    'Date': message_headers.get('Date'),
                    'Body': body.as_string()
                }
                decoded_email_params = EmailDecoder.decode_email(raw_email_params)
                html_content = EmailDecoder.email_to_html(decoded_email_params)
                email_html_to_image.apply_async(args=[html_content],
                                                link=send_image_to_telegram_task.s(self.redis_ops.telegram_id))
        else:
            logger.error('error %s' % response)
        return uid

    async def fetch_message_body(self, uid: int) -> Message:
        """Получение тела письма."""
        if self.connection_manager.client:
            try:
                dwnld_resp = await self.connection_manager.client.uid('fetch', str(uid), 'BODY.PEEK[]')
            except asyncio.exceptions.TimeoutError:
                logger.error(f'Fetching body failed for user {self.connection_manager.user}.'
                             f'IMAP server {self.connection_manager.host}.')
                raise IMAPServerTimeout
            return BytesParser().parsebytes(dwnld_resp.lines[1])
        else:
            raise IMAPClientIsNotConnected

    async def handle_server_push(self, push_messages: Collection[bytes]) -> str:
        """Обработка сообщений от IMAP сервера."""
        for msg in push_messages:
            if msg.endswith(b'EXISTS'):
                logger.info('new message: %r' % msg)
                return msg.split()[0].decode('utf-8')
            elif msg.endswith(b'EXPUNGE'):
                logger.info('message removed: %r' % msg)
            elif b'FETCH' in msg and br'\Seen' in msg:
                logger.info('message seen %r' % msg)
            else:
                logger.info('unprocessed push message : %r' % msg)
        return ''

    async def handle_active_state(self) -> bool:
        """Обработка активного статуса IMAP клиента."""
        if not self.connection_manager.client:
            raise IMAPClientIsNotConnected
        logger.info(f'{self.connection_manager.user} starting idle')
        try:
            idle_task = await self.connection_manager.client.idle_start(timeout=60)
            seq_number = await self.handle_server_push(
                await self.connection_manager.client.wait_server_push())
            self.connection_manager.client.idle_done()
            await wait_for(idle_task, timeout=20)
            if seq_number:
                uid = await self.fetch_uid_from_seq_number(seq_number)
                if uid:
                    self.persistent_max_uid = await self.fetch_messages_headers(uid)
                logger.info(f'Processed email with UID: {uid}')
                return True
        except asyncio.exceptions.TimeoutError:
            raise IMAPServerTimeout
        logger.info(f'{self.connection_manager.user} ending idle')
        return False

    async def imap_loop(self, initial_state: str = IMAPStatuses.ACTIVE.value) -> None:
        """Цикл поддержания состояния 'idle' с сервером."""
        await self.redis_ops.set_status(initial_state)
        await self.connection_manager.connect()
        if not self.connection_manager.client:
            raise IMAPClientIsNotConnected
        while True:
            current_status = await self.redis_ops.get_status()
            if current_status == IMAPStatuses.PAUSED.value:
                logger.info(
                    f'IMAPClient for {self.connection_manager.user} is in paused state. Awaiting active state...')
                await asyncio.sleep(5)
                continue
            elif current_status == IMAPStatuses.ACTIVE.value:
                await self.handle_active_state()
            elif current_status == IMAPStatuses.STOPPED.value:
                logger.info(f'IMAPClient for {self.connection_manager.user} stopped.')
                break
        await self.redis_ops.remove_status()
        await self.connection_manager.disconnect()
