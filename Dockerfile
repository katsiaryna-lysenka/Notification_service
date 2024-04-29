# Используем базовый образ Python
FROM python:3.10.12-slim

COPY pyproject.toml poetry.lock ./

# Устанавливаем зависимости
RUN apt-get update &&  \
    apt-get install -y --no-install-recommends gcc && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --only main

# Копируем исходный код в контейнер
COPY . /app

# Устанавливаем рабочую директорию
WORKDIR /app

# Запускаем main.py при старте контейнера
CMD ["python", "-u", "main.py"]

