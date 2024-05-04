from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.rebbitmq_file import AMQPConnectionError, consume_reset_email_messages


@pytest.mark.asyncio
async def test_consume_reset_email_messages_successful():
    mock_connection = AsyncMock()

    async def mock_message_processing(session, message_body):
        return True

    with patch(
        "src.rebbitmq_file.aio_pika.connect_robust", return_value=mock_connection
    ), patch(
        "src.rebbitmq_file.process_message", side_effect=mock_message_processing
    ), patch(
        "src.rebbitmq_file.validate_message", return_value=True
    ):

        result = await consume_reset_email_messages(Mock())

        assert result is True


@pytest.mark.asyncio
async def test_consume_reset_email_messages_invalid_message():
    mock_connection = AsyncMock()

    async def mock_message_processing(session, message_body):
        return True

    with patch(
        "src.rebbitmq_file.aio_pika.connect_robust", return_value=mock_connection
    ), patch(
        "src.rebbitmq_file.process_message", side_effect=mock_message_processing
    ), patch(
        "src.rebbitmq_file.validate_message", return_value=False
    ):

        result = await consume_reset_email_messages(Mock())

        assert result is True


@pytest.mark.asyncio
async def test_consume_reset_email_messages_connection_error():
    with patch(
        "src.rebbitmq_file.aio_pika.connect_robust",
        side_effect=AMQPConnectionError("Connection error"),
    ):

        result = await consume_reset_email_messages(Mock())

        assert result is None
