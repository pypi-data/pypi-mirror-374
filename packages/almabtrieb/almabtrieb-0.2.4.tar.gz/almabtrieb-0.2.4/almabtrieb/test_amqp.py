import pytest

from unittest.mock import MagicMock

from .amqp import AmqpConnection, response_regex, error_regex


def is_aio_pika_installed():
    try:
        import aio_pika  # noqa

        return True
    except ImportError:
        return False


@pytest.mark.skipif(not is_aio_pika_installed(), reason="aiopoka not installed")
def test_connected():
    connection = AmqpConnection(MagicMock(), "name")

    assert not connection.connected


def test_response_regex():
    assert response_regex.match("receive.alice.response.fetch")

    assert not response_regex.match("receive.alice.incoming")
    assert not response_regex.match("receive.alice.incoming.test")

    assert error_regex.match("error.alice")
