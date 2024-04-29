import json
import asyncio
import os
from datetime import datetime
from pymongo import MongoClient
import aio_pika
import boto3
from dotenv import load_dotenv

load_dotenv(".env")


MONGODB_URI = "mongodb://user:admin@mongodb:27017/"
AWS_REGION = "us-east-1"
AWS_SECRET_KEY_ID = os.getenv("AWS_SECRET_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_SES_SENDER = os.getenv("AWS_SES_SENDER")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")


async def process_reset_email_message(email: str, reset_token: str):
    message_body = {
        "email": email,
        "reset_token": reset_token,
        "subject": "Reset Your Password",
        "body": f"Reset your password by clicking the following link: "
                f"http://127.0.0.1:5000/auth/set-new-password?token={reset_token}\nThe link will deactivate in"
                f" 5 minutes",
        "published_at": datetime.utcnow()
    }
    print("Processing message:", message_body)

    # Create a MongoDB client
    client = MongoClient(MONGODB_URI)

    try:
        # Start a session
        with client.start_session() as session:
            # Start a transaction
            with session.start_transaction():
                # Save message to MongoDB
                db = client["reset_password_db"]
                messages_collection = db["reset_password_messages"]
                message_id = messages_collection.insert_one(message_body).inserted_id

                # Send email with AWS SES
                try:
                    ses_client = boto3.client(
                        "ses",
                        region_name=AWS_REGION,
                        aws_access_key_id=AWS_SECRET_KEY_ID,
                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
                    )
                    response = ses_client.send_email(
                        Source=AWS_SES_SENDER,
                        Destination={"ToAddresses": [email]},
                        Message={
                            "Subject": {"Data": message_body["subject"]},
                            "Body": {"Text": {"Data": message_body["body"]}}
                        }
                    )
                    print("Email sent successfully:", response)
                except Exception as e:
                    print("Error sending email:", e)
                    # Rollback transaction if email sending fails
                    session.abort_transaction()
                    return

                # Commit transaction if email sending is successful
                session.commit_transaction()

    except Exception as e:
        print("Error processing message:", e)
    finally:
        client.close()


async def consume_reset_email_messages():
    print("aaaaaaaaaaaaaaaaaaaaa")
    connection = None
    try:
        # connection = await aio_pika.connect_robust(
        #     f"amqp://user:12345@{settings.rabbitmq_host}/"
        # )
        rabbitmq_host = os.getenv('RABBITMQ_HOST')
        print(f"Connecting to RabbitMQ at {rabbitmq_host}")
        connection = await aio_pika.connect_robust(
            f"amqp://user:12345@{RABBITMQ_HOST}/"
        )
        print("bbbbbbbbbbbbbbbbbbbbbbbbb")

    except Exception as e:
        print("Type of exception:", type(e))

    except aio_pika.exceptions.AMQPConnectionError as e:
        print("cccccccccccccccccccc")
        error_message = f"Error connecting to RabbitMQ: {str(e)}"

        return error_message

    async with connection:
        print("dddddddddddddddddddddd")
        channel = await connection.channel()
        print("iiiiiiiiiiiiiiiiiiiiii")
        queue = await channel.declare_queue(
            "reset-password-stream", durable=True
        )
        print("eeeeeeeeeeeeeeeeee")
        async for message in queue:
            async with message.process():
                try:
                    message_body = json.loads(message.body)
                    print("Received message:")
                    print(message_body)

                except json.JSONDecodeError as e:

                    print("Failed to decode JSON:", e)

                except Exception as e:

                    print("An unexpected error occurred:", e)

        await queue.consume(process_reset_email_message)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(consume_reset_email_messages())
    loop.run_forever()

