import json
from aio_pika.exceptions import AMQPConnectionError
import aio_pika

from src.mongodb_file import process_message


async def consume_reset_email_messages():
    print("Consuming messages from reset-password-stream...")
    connection = None
    try:
        connection = await aio_pika.connect_robust("amqp://user:12345@rabbitmq:5672/")
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
                        # Validate message
                        if validate_message(message_body):
                            # Process message
                            success = await process_message(message_body)
                            if not success:
                                await queue.nack(message)
                        else:
                            print("Invalid message:", message_body)
                    except json.JSONDecodeError as e:
                        print("Failed to decode JSON:", e)
                        await queue.nack(message)
                    except Exception as e:
                        print("An unexpected error occurred:", e)
                        await queue.nack(message)

    except AMQPConnectionError as e:
        print("Error connecting to RabbitMQ:", e)
    except Exception as e:
        print("An unexpected error occurred:", e)
    finally:
        if connection is not None:
            await connection.close()


def validate_message(message):
    # Implement your validation logic here
    return True



