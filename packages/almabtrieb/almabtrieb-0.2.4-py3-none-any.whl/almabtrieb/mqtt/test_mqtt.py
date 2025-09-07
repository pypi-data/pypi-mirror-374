import pytest

from . import MqttConnection


def is_mqtt_installed():
    try:
        import aiomqtt  # noqa

        return True
    except ImportError:
        return False


@pytest.mark.skipif(not is_mqtt_installed(), reason="aiomqtt not installed")
def test_from_connection_string():
    connection = MqttConnection.from_connection_string("ws://user:pass@host/ws")

    assert isinstance(connection, MqttConnection)


@pytest.mark.skipif(not is_mqtt_installed(), reason="aiomqtt not installed")
def test_from_connection_string_echo():
    connection = MqttConnection.from_connection_string(
        "ws://user:pass@host/ws", echo=True
    )

    assert isinstance(connection, MqttConnection)
