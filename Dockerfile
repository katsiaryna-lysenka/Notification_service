# Используем базовый образ Python
FROM python:3.10.12-slim

# Устанавливаем зависимости
RUN pip install aio_pika pymongo boto3

# Копируем исходный код в контейнер
COPY . /app

# Устанавливаем рабочую директорию
WORKDIR /app

# Запускаем main.py при старте контейнера
CMD ["python", "main.py"]
