import os
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

load_dotenv(".env")


AWS_REGION = "us-east-1"
AWS_SECRET_KEY_ID = os.getenv("AWS_SECRET_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_SES_SENDER = os.getenv("AWS_SES_SENDER")


async def send_email(subject, body, recipient):
    message = MIMEMultipart()
    message["From"] = AWS_SES_SENDER
    message["To"] = recipient
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))
    try:
        with smtplib.SMTP("email-smtp.us-east-1.amazonaws.com", 587) as server:
            server.starttls()
            server.login(AWS_SECRET_KEY_ID, AWS_SECRET_ACCESS_KEY)
            server.sendmail(AWS_SES_SENDER, recipient, message.as_string())
        return True
    except Exception as e:
        print("Failed to send email:", e)
        return False
