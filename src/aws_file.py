import os
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import boto3

load_dotenv(".env")


AWS_REGION = "us-east-1"
AWS_SECRET_KEY_ID = os.getenv("AWS_SECRET_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_SES_SENDER = os.getenv("AWS_SES_SENDER")


def create_s3_bucket(bucket_name):
    print("asasasasas")
    s3_client = boto3.client("s3", endpoint_url="http://localstack:4566")
    print("dfdfdfdfdf")
    s3_client.create_bucket(Bucket=bucket_name)
    print("hghghghgh")


async def send_email(subject, body, recipient):
    print("111111111111111111")
    message = MIMEMultipart()
    print(f"message = {message}")
    message["From"] = AWS_SES_SENDER
    print(f" message['From'] = { message['From']}")
    message["To"] = recipient
    print(f"message['To'] = {message['To']}")
    message["Subject"] = subject
    print(f"message['Subject'] = {message['Subject']}")
    message.attach(MIMEText(body, "plain"))
    print("22222222222222")
    try:
        create_s3_bucket("my-test-bucket")  # Создание ведра S3
        print("S3 bucket created successfully")
        print("33333333333333333333333")
        with smtplib.SMTP("localstack", 4566) as server:
            print("4444444444444444444444444")
            server.starttls()
            print(f"message = {message}")
            server.login(AWS_SECRET_KEY_ID, AWS_SECRET_ACCESS_KEY)
            print(f"message = {message}")
            server.sendmail(AWS_SES_SENDER, recipient, message.as_string())
            print(f"message = {message}")
        return True
    except Exception as e:
        print("Failed to send email:", e)
        return False
