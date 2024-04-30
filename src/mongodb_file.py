import json

from pymongo import MongoClient, errors
from src.aws_file import send_email

#MONGODB_URI = "mongodb://user:12345@mongodb:27017/"
MONGODB_URI = "mongodb://mongodb-container:27017/?retryWrites=true&w=majority"
MAX_FAILURES = 5


async def process_message(message):
    failures = 0
    while failures < MAX_FAILURES:
        try:
            # Save message to MongoDB
            print("aaaaaaaa")
            client = MongoClient(MONGODB_URI)
            print("bbbbbbbbb")
            db = client["reset_password_db"]
            print("cccccccccccc")
            collection = db["reset_password_collection"]
            print(f"collection = {collection}")
            print(f"message = {message}")
            result = collection.insert_one(message)
            print("eeeeeeeeeeeeee")
            message_id = result.inserted_id
            print("Message saved to MongoDB with ID:", message_id)

            # Send email
            subject = "Instructions for changing your password"
            print(f"subject = {subject}")
            body = message.get("message")
            print(f"body = {body}")
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

    print(f"Failed to process message after {MAX_FAILURES} attempts")
    return False
