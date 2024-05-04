import json
import os

import aio_pika
from dotenv import load_dotenv
from pymongo import errors

from src.aws_file import send_email

load_dotenv(".env")

MONGO_HOST = os.getenv("MONGO_HOST")
MONGO_PORT = os.getenv("MONGO_PORT")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_USERNAME = os.getenv("RABBITMQ_USERNAME")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD")

MAX_FAILURES = 5


async def process_message(session, message):
    failures = 0
    while failures < MAX_FAILURES:
        try:
            # Save message to MongoDB
            db = session.client["reset_password_db"]
            collection = db["reset_password_collection"]
            result = collection.insert_one(message)
            message_id = result.inserted_id
            print("Message saved to MongoDB with ID:", message_id)

            # Send email
            subject = "Instructions for changing your password"
            body = message.get("message")
            print(f"{body=}")
            recipient = message.get("email")
            print(f"recipient = {recipient}")
            success = await send_email(subject, body, recipient)
            print(f"success = {success}")

            if success:
                print("Email sent successfully")
                return True
            else:
                print("Failed to send email")
                failures += 1
        except errors.PyMongoError as e:
            print("Failed to save message to MongoDB:", e)
            failures += 1

    if failures == MAX_FAILURES:
        print(
            f"Failed to process message after {MAX_FAILURES} attempts. "
            f"Sending to dead letter queue."
        )
        await send_to_dead_letter_queue(session, message)
    return False


async def send_to_dead_letter_queue(session, message):
    try:
        dlq_connection = await aio_pika.connect_robust(
            f"amqp://{RABBITMQ_USERNAME}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:5672/"
        )
        async with dlq_connection:
            dlq_channel = await dlq_connection.channel()
            dlq_queue = await dlq_channel.declare_queue(
                "dead-letter-queue", durable=True
            )

            await dlq_queue.publish(json.dumps(message))

            print("Message sent to dead letter queue successfully")
            return True

    except Exception as e:
        print(f"Failed to send message to dead letter queue: {e}")
        return False
