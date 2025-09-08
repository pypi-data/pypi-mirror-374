import pytest

from almabtrieb.util import parse_connection_string

from .base import MqttBaseConnection
from .test_mqtt import is_mqtt_installed


@pytest.mark.skip(
    reason="Testing connectivity only possible when MQTT broker is available"
)
async def test_base_mqtt():
    parsed = parse_connection_string("mqtt://almabtrieb:password@localhost:11883")

    connection = MqttBaseConnection(**parsed)

    async with connection.run(topics_to_subscribe=[]):
        assert connection.connected


@pytest.mark.skipif(not is_mqtt_installed(), reason="aiomqtt not installed")
async def test_mqtts():
    parsed = parse_connection_string("mqtts://test.mosquitto.org:8883")

    connection = MqttBaseConnection(**parsed)

    async with connection.run(topics_to_subscribe=[]):
        assert connection.connected
