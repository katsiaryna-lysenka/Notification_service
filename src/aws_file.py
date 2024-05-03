import os

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv(".env")


AWS_REGION = "us-east-1"
AWS_SECRET_KEY_ID = os.getenv("AWS_SECRET_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_SES_SENDER = os.getenv("AWS_SES_SENDER")
S3_BASE_URL = os.getenv("S3_BASE_URL")


def create_s3_bucket(bucket_name):
    try:

        s3_base_url = S3_BASE_URL
        aws_access_key_id = AWS_SECRET_KEY_ID
        aws_secret_access_key = AWS_SECRET_ACCESS_KEY

        # Создаем клиент S3 для LocalStack
        s3_client = boto3.client(
            "s3",
            endpoint_url=s3_base_url,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            verify=False,
        )

        s3_client.create_bucket(Bucket=bucket_name)

        print(f"S3 bucket '{bucket_name}' created in LocalStack.")
        return True
    except ClientError as e:
        print(f"Error during creation (bucket) '{bucket_name}': {e}")
        return False
    except Exception as e:
        print("It was an error during creation (bucket):", e)
        return False


async def send_email(subject, body, recipient):

    message = {"Subject": {"Data": subject}, "Body": {"Text": {"Data": body}}}

    try:
        create_s3_bucket("my-test-bucket")
        print("S3 bucket created successfully")

        # Инициализация клиента SES для LocalStack
        ses_client = boto3.client(
            "ses",
            region_name=AWS_REGION,
            endpoint_url=S3_BASE_URL,  # URL LocalStack
            aws_access_key_id=AWS_SECRET_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            verify=False,
        )

        response = ses_client.verify_email_identity(EmailAddress=AWS_SES_SENDER)

        print(f"Email address verified successfully, response = {response}")

        # Send email during SES
        response = ses_client.send_email(
            Source=AWS_SES_SENDER,
            Destination={"ToAddresses": [recipient]},
            Message=message,
        )

        print(f"response = {response}")
        print("Email sent successfully")
        return True
    except ClientError as e:
        print(f"Failed to send email: {e.response['Error']['Message']}")
        return False
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
