import base64
import json
import os
from http import HTTPStatus
from io import BytesIO

import requests
from celery import shared_task
from django.conf import settings
from html2image import Html2Image
from infrastructure.gateways.redis_client import redis_client
from infrastructure.utils.send_bot import send_photo_to_telegram_sync
from PIL import Image, ImageOps


@shared_task(bind=True)
def send_failed_emails_to_telegram(self) -> None:
    """
    Попытка переотправки всех неотправленных emails.
    Задача извлекает все недоставленные письма из Redis и отправляет их в Telegram.
    После успешной отправки письмо удаляется из Redis.
    """
    all_keys = redis_client.get_all_keys(pattern='telegram_id_*_failed_emails')
    for key in all_keys:
        failed_emails = redis_client.get_list_all_items(key)
        if failed_emails:
            for email in failed_emails:
                data = json.loads(email)
                response = requests.post(settings.TELEGRAM_SEND_MESSAGE_URL, data=data)
                if response.status_code == HTTPStatus.OK:
                    redis_client.lpop(key)


@shared_task(bind=True)
def send_failed_photos_to_telegram(self) -> None:
    """
    Попытка переотправки всех неотправленных photos.
    Задача извлекает все недоставленные фото из Redis и отправляет их в Telegram.
    После успешной отправки фото удаляется из Redis.
    """
    all_keys = redis_client.get_all_keys(pattern='telegram_id_*_failed_photos')
    for key in all_keys:
        failed_photo_data_list = redis_client.get_list_all_items(key)
        if failed_photo_data_list:
            for failed_photo_data in failed_photo_data_list:
                photo_data = json.loads(failed_photo_data)
                chat_id = photo_data['data']['chat_id']
                image_bytes = base64.b64decode(photo_data['image'])
                data = {
                    'chat_id': chat_id
                }
                files = {
                    'photo': image_bytes
                }
                response = requests.post(settings.TELEGRAM_SEND_PHOTO_URL, data=data,
                                         files=files)

                if response.status_code == HTTPStatus.OK:
                    redis_client.lpop(key)


@shared_task(bind=True)
def email_html_to_image(self, html_content: str) -> bytes:
    """Задача, которая создает картинку и преобразует её в байты."""
    hti = Html2Image()
    temp_file_path = 'temp_email_image.png'
    hti.screenshot(html_str=html_content, save_as=temp_file_path, size=(1200, 1000))
    with Image.open(temp_file_path) as img:
        bbox = ImageOps.invert(img.convert('RGB')).getbbox()
        img_cropped = img.crop(bbox)
        img_bytes = BytesIO()
        img_cropped.save(img_bytes, format='PNG')
        img_bytes = img_bytes.getvalue()  # type: ignore
    os.remove(temp_file_path)
    return img_bytes  # type: ignore


@shared_task(bind=True)
def send_image_to_telegram_task(self, image_bytes: bytes, telegram_id: int) -> None:
    """Задача, которая отправляет сообщение в телеграм."""
    send_photo_to_telegram_sync(image_bytes, telegram_id)
