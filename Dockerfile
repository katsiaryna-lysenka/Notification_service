FROM python:3.10.12-slim AS builder

LABEL authors="user"

WORKDIR /app

COPY pyproject.toml poetry.lock ./

# Устанавливаем зависимости
RUN apt-get update &&  \
    apt-get install -y --no-install-recommends gcc && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --only main


FROM builder

# Устанавливаем рабочую директорию
WORKDIR /app

COPY --from=builder /usr/local/lib/python3.10/site-packages/ /usr/local/lib/python3.10/site-packages/
COPY --from=builder /usr/local/bin/poetry /usr/local/bin/poetry

# Копируем исходный код в контейнер
COPY . /app

EXPOSE 8000

# Запускаем main.py при старте контейнера
CMD ["python", "-u", "main.py"]

