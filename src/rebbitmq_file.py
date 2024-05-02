import json
import os
import aio_pika

from dotenv import load_dotenv
from aio_pika.exceptions import AMQPConnectionError
from src.mongodb_file import process_message

load_dotenv(".env")

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_USERNAME = os.getenv("RABBITMQ_USERNAME")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD")


async def consume_reset_email_messages(session):
    print("Consuming messages from reset-password-stream...")
    connection = None
    try:
        connection = await aio_pika.connect_robust(f"amqp://{RABBITMQ_USERNAME}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:5672/")
        print("Connected to RabbitMQ")
        async with connection:
            channel = await connection.channel()
            queue = await channel.declare_queue("reset-password-stream", durable=True)
            async for message in queue:
                async with message.process():
                    try:
                        message_body = json.loads(message.body)
                        print("Received message:")
                        print(message_body)

                        if validate_message(message_body):
                            # Process message
                            success = await process_message(session, message_body)
                            if not success:
                                await queue.nack(message)
                                return False
                        else:
                            print("Invalid message:", message_body)
                    except json.JSONDecodeError as e:
                        print("Failed to decode JSON:", e)
                        await queue.nack(message)
                    except Exception as e:
                        print("An unexpected error occurred:", e)
                        await queue.nack(message)

            print("All messages processed successfully")
            return True

    except AMQPConnectionError as e:
        print("Error connecting to RabbitMQ:", e)
    except Exception as e:
        print("An unexpected error occurred:", e)
    finally:
        if connection is not None:
            await connection.close()


def validate_message(message):
    required_keys = ['email', 'reset_token', 'message']

    if all(key in message for key in required_keys):
        return True
    else:
        return False

