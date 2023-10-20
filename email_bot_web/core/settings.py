import operator
import os
from functools import reduce

from pathlib import Path

from celery.schedules import crontab

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY')

DEBUG = os.getenv('ENVIRONMENT') == 'dev'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', default='*').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'email_service',
    'user',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE'),
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('POSTGRES_HOST'),
        'PORT': os.getenv('POSTGRES_PORT')
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = '/web-static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'web-static')

MEDIA_URL = '/web-media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'web-media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')

CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'
CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'

TELEGRAM_HOST = os.getenv('TELEGRAM_HOST', '')
BOT_TOKEN = os.getenv('BOT_TOKEN', '')
CRYPTO_KEY = os.getenv('CRYPTO_KEY', '')
TELEGRAM_SEND_MESSAGE_URL = os.path.join(TELEGRAM_HOST, 'bot' + BOT_TOKEN, 'sendMessage')
TELEGRAM_SEND_PHOTO_URL = os.path.join(TELEGRAM_HOST, 'bot' + BOT_TOKEN, 'sendPhoto')

CACHE_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', 3600))  # in seconds
BOT_USER_KEY_FORMAT = 'bot_user_{telegram_id}'
ACTIVE_USERS_KEY_FORMAT = 'active_users'
USER_EXISTS_KEY_FORMAT = 'bot_user_exists_{telegram_id}'
EMAIL_SERVICE_KEY_FORMAT = 'email_service_{service_id}'
EMAIL_SERVICES_KEY_FORMAT = 'email_services'
BOX_FILTERS_KEY_FORMAT = 'box_filters_{box_id}'
EMAIL_BOX_KEY_FORMAT = 'email_box_{box_id}'
USER_EMAIL_BOXES_KEY_FORMAT = 'bot_user_{telegram_id}_email_boxes'
IMAP_CLIENT_STATUS_KEY_FORMAT = 'imap_client_status_{telegram_id}_{box_id}'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'infrastructure': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

CELERY_BEAT_SCHEDULE = {
    'send-emails-every-minute': {
        'task': 'email_service.tasks.send_failed_emails_to_telegram',
        'schedule': crontab(minute='*'),
    },
    'send-photos-every-minute': {
        'task': 'email_service.tasks.send_failed_photos_to_telegram',
        'schedule': crontab(minute='*'),
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://{os.getenv("REDIS_HOST")}:{os.getenv("REDIS_PORT")}/0',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
