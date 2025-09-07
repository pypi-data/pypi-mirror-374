import json
import logging

from almabtrieb.util import parse_connection_string
from almabtrieb.base import BaseConnection, ReceivedMessage, MessageType

from .base import MqttBaseConnection

logger = logging.getLogger(__name__)


class MqttConnection(BaseConnection):
    def __init__(
        self,
        base_connection: MqttBaseConnection,
        username: str,
        echo: bool = False,
        silent: bool = False,
    ):
        super().__init__(echo=echo, silent=silent)
        self.username = username
        self.base_connection = base_connection

    @staticmethod
    def from_connection_string(
        connection_string: str, echo: bool = False, silent: bool = False
    ) -> "MqttConnection":
        parsed = parse_connection_string(connection_string)
        return MqttConnection(
            base_connection=MqttBaseConnection(**parsed, echo=echo),
            echo=echo,
            username=parsed["username"],
            silent=silent,
        )

    @property
    def connected(self):
        return self.base_connection.connected

    @property
    def receive(self):
        return f"receive/{self.username}/#"

    @property
    def receive_error(self):
        return f"error/{self.username}"

    @property
    def send_topic(self):
        return f"send/{self.username}"

    async def run(self):
        try:
            async with self.base_connection.run(
                [self.receive, self.receive_error]
            ) as client:
                if client is None:
                    raise Exception("Client not initialized")

                try:
                    async for message in client.messages:
                        correlation_id = getattr(
                            message.properties, "CorrelationData"
                        ).decode()

                        if message.topic.matches("receive/+/response/+"):
                            message_type = MessageType.response
                        elif message.topic.matches("receive/+/incoming"):
                            message_type = MessageType.incoming
                        elif message.topic.matches("receive/+/outgoing"):
                            message_type = MessageType.outgoing
                        elif message.topic.matches("error/+"):
                            message_type = MessageType.error
                        else:
                            logger.warning("Unknown topic: %s", message.topic)
                            message_type = MessageType.unknown

                        payload = message.payload
                        if (
                            payload is None
                            or isinstance(payload, int)
                            or isinstance(payload, float)
                            or isinstance(payload, bytearray)
                        ):
                            logger.warning("Cannot handle payload")
                            continue

                        await self.handle(
                            ReceivedMessage(
                                message_type=message_type,
                                correlation_id=correlation_id,
                                data=json.loads(payload),
                            ),
                        )
                except Exception:
                    logger.warning("Mesage processing stopped")

        except Exception:
            logger.warning("Sending termination to listeners")
            await self.handle_termination()

    async def send(
        self, topic_end: str, data: dict, correlation_data: str | None = None
    ) -> str:
        topic = f"{self.send_topic}/{topic_end}"

        correlation_data = await self.base_connection.send(
            topic, data, correlation_data=correlation_data
        )

        return correlation_data
