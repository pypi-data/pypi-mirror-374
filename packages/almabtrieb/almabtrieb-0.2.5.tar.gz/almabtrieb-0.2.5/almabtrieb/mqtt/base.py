import logging
import json
import ssl

from uuid import uuid4
from typing import List

from contextlib import asynccontextmanager
from dataclasses import dataclass

logger = logging.getLogger(__name__)

try:
    from aiomqtt import Client

    from paho.mqtt.properties import Properties
    from paho.mqtt.packettypes import PacketTypes
    from paho.mqtt.enums import MQTTProtocolVersion

    @dataclass
    class MqttBaseConnection:  # type: ignore
        host: str
        port: int

        username: str
        password: str
        path: str
        protocol: str

        echo: bool = False
        client: Client | None = None

        connected: bool = False
        keepalive: int = 50
        timeout: int = 10

        @property
        def transport(self):
            if self.protocol in ["mqtt", "mqtts"]:
                return "tcp"
            else:
                return "websockets"

        @asynccontextmanager
        async def run(self, topics_to_subscribe: List[str]):
            if self.protocol in ["wss", "mqtts"]:
                tls_context = ssl.SSLContext(protocol=ssl.PROTOCOL_TLS)
            else:
                tls_context = None
            self.client = Client(
                self.host,
                port=self.port,
                transport=self.transport,
                username=self.username,
                password=self.password,
                websocket_path=self.path,
                keepalive=self.keepalive,
                tls_context=tls_context,
                timeout=self.timeout,
                protocol=MQTTProtocolVersion.MQTTv5,
            )
            async with self.client:
                self.connected = True
                for topic in topics_to_subscribe:
                    await self.client.subscribe(topic)
                logger.info("Connected to %s as %s", self.host, self.username)

                yield self.client

        async def send(
            self, topic: str, data: dict, correlation_data: str | None = None
        ) -> str:
            if correlation_data is None:
                correlation_data = str(uuid4())
            properties = Properties(PacketTypes.PUBLISH)
            properties.CorrelationData = correlation_data.encode()

            if self.echo:
                logger.info("%s: %s, %s", topic, correlation_data, json.dumps(data))

            if self.client is None:
                raise ValueError("Client not initialized")

            await self.client.publish(topic, json.dumps(data), properties=properties)

            return correlation_data

except ImportError:

    class MqttBaseConnection:
        @staticmethod
        def from_connection_string(connection_string: str, echo: bool):
            raise NotImplementedError("please install aiomqtt")

        def __init__(self, *args, **kwargs):
            raise NotImplementedError("please install aiomqtt")
