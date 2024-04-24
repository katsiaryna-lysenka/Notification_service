import docker
from pymongo import MongoClient
import boto3
import json
import socket
from datetime import datetime
from pymongo import MongoClient
import boto3
import pika

# Connect to MongoDB
client = MongoClient("mongodb://mongodb:27017")
db = client["pymongo"]
messages_collection = db["reset_password_messages"]

# Connect to AWS SES
ses_client = boto3.client("ses", region_name="us-east-1")
print(f"ses_client = {ses_client}")


# Define RabbitMQ connection parameters
rabbitmq_host = "rabbitmq-container"
rabbitmq_user = "user"
rabbitmq_pass = "12345"
rabbitmq_queue = "reset-password-stream"


def handle_message(channel, method, properties, body):
    try:
        message_body = json.loads(body)
        validate_message(message_body)

        # Save message to MongoDB
        message_id = messages_collection.insert_one({
            "user_id": message_body.get("user_id"),
            "email": message_body["email"],
            "subject": message_body["subject"],
            "body": message_body["body"],
            "published_at": datetime.utcnow()
        }).inserted_id

        # Send email using AWS SES
        send_email(message_body["email"], message_body["reset_token"], message_body["subject"], message_body["body"])

        # Acknowledge message
        channel.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        # Handle error
        print(f"Error handling reset password message: {e}")
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)  # Reject the message without requeuing


def validate_message(message_body: dict):
    # Implement message validation logic here
    if "email" not in message_body or "reset_token" not in message_body:
        raise ValueError("Invalid reset password message format")


def send_email(email: str, reset_token: str, subject: str, body: str):
    try:
        # Send email using AWS SES
        response = ses_client.send_email(
            Source="your@email.com",
            Destination={"ToAddresses": [email]},
            Message={
                "Subject": {"Data": subject},
                "Body": {"Text": {"Data": body}},
            },
        )

        print(f"Reset password email sent successfully: {response['MessageId']}")

    except Exception as e:
        # Handle error
        print(f"Failed to send email: {e}")
        raise RuntimeError("Failed to send email")


def consume_messages():
    try:
        rabbitmq_ip = socket.gethostbyname('rabbitmq-container')

        # Use the IP address in the connection parameters
        credentials = pika.PlainCredentials('user', '12345')
        parameters = pika.ConnectionParameters(rabbitmq_ip, 5672, '/', credentials)
        # credentials = pika.PlainCredentials('user', '12345')
        # parameters = pika.ConnectionParameters('rabbitmq-container',
        #                                        5672,
        #                                        '/',
        #                                        credentials)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_declare(queue="reset-password-stream", durable=True)
        channel.basic_qos(prefetch_count=1)  # Receive one message at a time

        channel.basic_consume(queue="reset-password-stream", on_message_callback=handle_message)
        print('Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()
    except pika.exceptions.AMQPConnectionError as e:
        print(f"Error connecting to RabbitMQ: {e}")


if __name__ == "__main__":
    consume_messages()
