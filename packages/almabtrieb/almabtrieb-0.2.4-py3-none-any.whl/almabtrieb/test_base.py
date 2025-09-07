from .base import BaseConnection


async def test_termination():
    connection = BaseConnection()

    await connection.handle_termination()
