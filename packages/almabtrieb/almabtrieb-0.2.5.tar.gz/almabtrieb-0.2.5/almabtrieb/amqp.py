from uuid import uuid4
import json
import logging
import re

from .base import BaseConnection, ReceivedMessage, MessageType
from .util import censor_password

logger = logging.getLogger(__name__)

response_regex = re.compile(r"^receive.\w+\.response\.\w+$")
incoming_regex = re.compile(r"^receive.\w+\.incoming$")
outgoing_regex = re.compile(r"^receive.\w+\.outgoing$")
error_regex = re.compile(r"^error.\w+$")

try:
    import aio_pika

    class AmqpConnection(BaseConnection):  # type: ignore
        def __init__(
            self,
            connection_string: str,
            username: str,
            echo: bool = False,
            silent: bool = False,
            timeout: int | None = 10,
        ):
            super().__init__(echo=echo, silent=silent)

            self.connection_string = connection_string
            self.channel = None
            self.username = username
            self.timeout = timeout

        @property
        def connected(self):
            return self.channel is not None

        @property
        def subscription_topic(self):
            return f"receive.{self.username}.#"

        @property
        def subscription_topic_error(self):
            return f"error.{self.username}"

        def routing_key(self, topic_end: str):
            """
            ```pycon
            >>> connection = AmqpConnection("amqp://guest:guest@localhost/", "alice")
            >>> connection.routing_key("example.one")
            'send.alice.example.one'

            >>> connection.routing_key("example/two")
            'send.alice.example.two'

            ```
            """

            return f"send.{self.username}.{topic_end.replace('/', '.')}"

        async def run(self):
            try:
                if not self.silent:
                    logger.info(
                        "Conneting to amqp with %s",
                        censor_password(self.connection_string),
                    )
                connection = await aio_pika.connect_robust(
                    self.connection_string, timeout=self.timeout
                )

                async with connection:
                    self.channel = await connection.channel()

                    await self.channel.set_qos(prefetch_count=1)
                    self.exchange = await self.channel.declare_exchange(
                        "amq.topic",
                        aio_pika.ExchangeType.TOPIC,
                        durable=True,
                    )

                    queue = await self.channel.declare_queue(
                        "almabtrieb_queue_" + str(uuid4()),
                        durable=False,
                        auto_delete=True,
                    )

                    await queue.bind(self.exchange, routing_key=self.subscription_topic)
                    await queue.bind(
                        self.exchange, routing_key=self.subscription_topic_error
                    )

                    async with queue.iterator() as iterator:
                        async for message in iterator:
                            async with message.process():
                                await self.handle_message(message)
            except Exception as e:
                self.handle_termination()
                logger.exception(e)

        async def handle_message(self, message):
            routing_key = message.routing_key

            if response_regex.match(routing_key):
                message_type = MessageType.response
            elif incoming_regex.match(routing_key):
                message_type = MessageType.incoming
            elif outgoing_regex.match(routing_key):
                message_type = MessageType.outgoing
            elif error_regex.match(routing_key):
                message_type = MessageType.error
            else:
                logger.info("Unknown routing key %s", routing_key)
                message_type = MessageType.unknown

            await self.handle(
                ReceivedMessage(
                    message_type=message_type,
                    correlation_id=message.correlation_id,
                    data=json.loads(message.body),
                ),
            )

        async def send(
            self, topic_end: str, data: dict, correlation_data: str | None = None
        ) -> str:
            if correlation_data is None:
                correlation_data = str(uuid4())
            await self.exchange.publish(
                aio_pika.Message(
                    body=json.dumps(data).encode(),
                    correlation_id=correlation_data,
                ),
                routing_key=self.routing_key(topic_end),
            )

            if self.echo:
                logger.info(
                    "Sent %s %s",
                    self.routing_key(topic_end),
                    json.dumps(data, indent=2),
                )

            return correlation_data

except ImportError:

    class AmqpConnection:
        def __init__(self, *args, **kwargs):
            raise ImportError("aio_pika is not installed")
