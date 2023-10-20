import base64
import json
from http import HTTPStatus
from typing import Any

import httpx
import requests
from django.conf import settings
from infrastructure.gateways.redis_client import redis_client

MAX_MESSAGE_LENGTH = 1000


async def send_email_to_telegram(email_data: dict[str, Any], telegram_id: int) -> dict[str, str]:
    """Асинхронное отправление пиьсма в телеграм."""
    formatted_message = (
        f"Subject: {email_data['Subject']}\n"
        f"From: {email_data['From']}\n"
        f"To: {email_data['To']}\n"
        f"Date: {email_data['Date']}\n"
        f"Body: {email_data['Body']['text_body']}"
    )
    if len(formatted_message) > MAX_MESSAGE_LENGTH:
        formatted_message = formatted_message[:MAX_MESSAGE_LENGTH] + '... (truncated)'
    data = {
        'chat_id': telegram_id,
        'text': formatted_message
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(settings.TELEGRAM_SEND_MESSAGE_URL, data=data)
    if response.status_code != HTTPStatus.OK:
        redis_key = f'telegram_id_{telegram_id}_failed_emails'
        redis_client.prepend_to_list(redis_key, json.dumps(data))
        redis_client.touch(redis_key, timeout=86400)
    return response.json()


async def send_photo_to_telegram(image_bytes: bytes, telegram_id: int) -> dict[str, str]:
    """Асинхронное отправление картинки в телеграм."""
    data = {
        'chat_id': telegram_id
    }
    files = {
        'photo': image_bytes
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(settings.TELEGRAM_SEND_PHOTO_URL, data=data, files=files)
    if response.status_code != HTTPStatus.OK:
        redis_key = f'telegram_id_{telegram_id}_failed_photos'
        failed_data = {
            'data': data,
            'image': base64.b64encode(image_bytes).decode('utf-8')
        }
        redis_client.prepend_to_list(redis_key, json.dumps(failed_data))
        redis_client.touch(redis_key, timeout=86400)
    return response.json()


def send_photo_to_telegram_sync(image_bytes: bytes, telegram_id: int) -> dict[str, str]:
    """Синхронное отправление картинки в телеграм."""
    data = {
        'chat_id': telegram_id
    }
    files = {
        'photo': image_bytes
    }
    response = requests.post(settings.TELEGRAM_SEND_PHOTO_URL, data=data, files=files)
    if response.status_code != HTTPStatus.OK:
        redis_key = f'telegram_id_{telegram_id}_failed_photos'
        failed_data = {
            'data': data,
            'image': base64.b64encode(image_bytes).decode('utf-8')
        }
        redis_client.prepend_to_list(redis_key, json.dumps(failed_data))
        redis_client.touch(redis_key, timeout=86400)
    return response.json()
