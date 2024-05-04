from unittest.mock import Mock, patch

import pytest

from mongodb_file import send_to_dead_letter_queue


@pytest.mark.asyncio
async def test_send_to_dead_letter_queue_failure():
    with patch("aio_pika.connect_robust", side_effect=Exception("Connection error")):
        message = {"message": "Reset your password", "email": "test@example.com"}

        result = await send_to_dead_letter_queue(Mock(), message)

        assert result is False


@pytest.mark.asyncio
async def test_send_to_dead_letter_queue_successful():
    async def mock_publish(*args, **kwargs):
        return True

    with patch("aio_pika.connect_robust") as mock_connect_robust:
        mock_connection = mock_connect_robust.return_value.__aenter__.return_value
        mock_channel = mock_connection.channel.return_value
        mock_queue = mock_channel.declare_queue.return_value

        mock_queue.publish = mock_publish

        message = {"message": "Reset your password", "email": "katy@example.com"}

        result = await send_to_dead_letter_queue(Mock(), message)

        assert result is True
