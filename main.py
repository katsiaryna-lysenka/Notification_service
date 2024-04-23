import asyncio
from datetime import datetime
from typing import Dict
from pymongo import MongoClient
import boto3
import pika
import json
# Connect to MongoDB
client = MongoClient("mongodb://mongodb:27017")
db = client["pymongo"]
messages_collection = db["reset_password_messages"]

# Connect to AWS SES
ses_client = boto3.client("ses", region_name="us-east-1")


def handle_reset_password_message(message: dict):
    try:
        # Validate message
        if "email" not in message or "reset_token" not in message:
            raise ValueError("Invalid reset password message format")

        # Construct email message
        subject = "Reset Your Password"
        body = f"Reset your password by clicking the following link: http://127.0.0.1:5000/auth/set-new-password?token={message['reset_token']}\nThe link will deactivate in 5 minutes"

        # Save message to MongoDB
        message_id = messages_collection.insert_one({
            "user_id": message.get("user_id"),
            "email": message["email"],
            "subject": subject,
            "body": body,
            "published_at": datetime.utcnow()
        }).inserted_id

        # Send email using AWS SES
        response = ses_client.send_email(
            Source="your@email.com",
            Destination={"ToAddresses": [message["email"]]},
            Message={
                "Subject": {"Data": subject},
                "Body": {"Text": {"Data": body}},
            },
        )

        print(f"Reset password email sent successfully: {response['MessageId']}")

    except Exception as e:
        # Handle error
        print(f"Error handling reset password message: {e}")


def send_email(email: str, reset_token: str):
    try:
        # Construct email message
        subject = "Reset Your Password"
        body = f"Reset your password by clicking the following link: http://127.0.0.1:5000/auth/set-new-password?token={reset_token}\nThe link will deactivate in 5 minutes"

        # Send email using AWS SES
        response = ses_client.send_email(
            Source="your@email.com",
            Destination={"ToAddresses": [email]},
            Message={
                "Subject": {"Data": subject},
                "Body": {"Text": {"Data": body}},
            },
        )

        print(f"Email sent successfully: {response['MessageId']}")

    except Exception as e:
        raise RuntimeError(f"Failed to send email: {e}")


def callback(ch, method, properties, body):
    # Decode JSON message body
    message_body = json.loads(body)
    print("Received message:", message_body)

    # Handle reset password message
    handle_reset_password_message(message_body)


def main():
    # Establish connection to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq-container'))
    channel = connection.channel()

    # Declare queue
    channel.queue_declare(queue='reset-password-stream', durable=True)

    # Start consuming messages from the queue
    channel.basic_consume(queue='reset-password-stream', on_message_callback=callback, auto_ack=True)

    print('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == "__main__":
    main()


