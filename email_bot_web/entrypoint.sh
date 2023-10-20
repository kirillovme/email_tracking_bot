#!/bin/bash

if [[ "${1}" == "web" ]]; then
    python3 manage.py migrate
    python3 manage.py collectstatic --noinput
    exec uvicorn core.asgi:application --host 0.0.0.0 --port "$WEB_PORT" --log-level debug
elif [[ "${1}" == "worker" ]]; then
    celery -A core worker --loglevel=info
elif [[ "${1}" == "beat" ]]; then
  celery -A core beat --loglevel=info
elif [[ "${1}" == "flower" ]]; then
    celery -A core flower
fi
