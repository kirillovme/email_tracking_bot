FROM python:3.10-slim

WORKDIR /bot

ENV PYTHONUNBUFFERED=1

COPY ./poetry.lock ./pyproject.toml ./

RUN pip install poetry==1.5.1

RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi --no-root --only main

COPY ./bot .

CMD ["python3", "main.py"]
