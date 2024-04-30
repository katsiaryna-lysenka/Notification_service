import asyncio

from src.rebbitmq_file import consume_reset_email_messages


if __name__ == "__main__":
    asyncio.run(consume_reset_email_messages())

