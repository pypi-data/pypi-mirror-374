import pytest
from unittest.mock import AsyncMock

from . import Almabtrieb


def test_unknown_connection_string():
    with pytest.raises(NotImplementedError):
        Almabtrieb.from_connection_string("unknown://user:pass@host/ws")


async def test_create_actor():
    almabtrieb = Almabtrieb(connection=AsyncMock())

    await almabtrieb.create_actor("http://host.example")

    almabtrieb.connection.send_with_reply.assert_awaited_once()  # type: ignore
