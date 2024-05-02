import os
from pymongo import MongoClient, errors
from dotenv import load_dotenv
from src.rebbitmq_file import consume_reset_email_messages

load_dotenv(".env")

MONGO_HOST = os.getenv("MONGO_HOST")
MONGO_PORT = os.getenv("MONGO_PORT")
MONGODB_URI = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/?retryWrites=true&w=majority"
client = MongoClient(MONGODB_URI)


async def execute_with_transaction():
    try:
        with client.start_session() as session:
            with session.start_transaction():
                try:

                    success = await consume_reset_email_messages(session)
                    if success:
                        session.commit_transaction()
                        print("Transaction committed successfully")
                    else:
                        session.abort_transaction()
                        print("Transaction aborted due to processing error in messages")
                except Exception as e:
                    session.abort_transaction()
                    print("Transaction aborted due to error:", e)
    except errors.PyMongoError as e:
        print("MongoDB error occurred:", e)
    except Exception as e:
        print("An unexpected error occurred:", e)
