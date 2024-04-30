from pymongo import MongoClient, errors
from src.aws_file import send_email

MONGODB_URI = "mongodb://user:admin@mongodb:27017/"
MAX_FAILURES = 5


async def process_message(message):
    failures = 0
    while failures < MAX_FAILURES:
        try:
            # Save message to MongoDB
            client = MongoClient(MONGODB_URI)
            db = client["reset_password_db"]
            collection = db["reset_password_collection"]
            result = collection.insert_one(message)
            message_id = result.inserted_id
            print("Message saved to MongoDB with ID:", message_id)

            # Send email
            subject = message.get("subject")
            body = message.get("body")
            recipient = message.get("email_address")
            success = await send_email(subject, body, recipient)

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
