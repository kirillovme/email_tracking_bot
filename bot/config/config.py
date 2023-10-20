import os

BOT_TOKEN = os.getenv('BOT_TOKEN', '')
CRYPTO_KEY = os.getenv('CRYPTO_KEY', '')
API_URL = os.getenv('API_URL', '')

USER_EXISTS_ENDPOINT = 'users/{telegram_id}/exists'
CREATE_USER_ENDPOINT = 'users'
CREATE_BOX_ENDPOINT = 'users/{telegram_id}/boxes'
DOMAIN_LIST_ENDPOINT = 'services'
GET_BOXES_ENDPOINT = 'users/{telegram_id}/boxes'
GET_BOX_ENDPOINT = 'users/{telegram_id}/boxes/{box_id}'
PAUSE_BOX_ENDPOINT = 'users/{telegram_id}/boxes/{box_id}/pause'
RESUME_BOX_ENDPOINT = 'users/{telegram_id}/boxes/{box_id}/resume'
DELETE_BOX_ENDPOINT = 'users/{telegram_id}/boxes/{box_id}'

API_ERROR = 'В настоящее время бот недоступен 😞'
