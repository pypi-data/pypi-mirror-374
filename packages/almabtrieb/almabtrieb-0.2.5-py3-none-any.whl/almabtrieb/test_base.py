from unittest.mock import AsyncMock
from .base import BaseConnection


async def test_termination():
    connection = BaseConnection()

    await connection.handle_termination()


async def test_termination_on_disconnect_awaited():
    on_disconnect = AsyncMock()
    connection = BaseConnection(on_disconnect=[on_disconnect])

    await connection.handle_termination()

    on_disconnect.assert_awaited_once()
