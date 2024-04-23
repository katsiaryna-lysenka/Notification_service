FROM python:3.9

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY poetry.lock pyproject.toml /app/
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

COPY . /app/

EXPOSE 8000

CMD ["python", "main.py"]