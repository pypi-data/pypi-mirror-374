import asyncio
import logging

from dataclasses import dataclass
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from .amqp import AmqpConnection
from .mqtt import MqttConnection
from .model import (
    InformationResponse,
    CreateActorRequest,
    FetchMessage,
    FetchResponse,
)
from .exceptions import NoIncomingException, ErrorMessageException
from .util import ConnectionParams

__all__ = ["Almabtrieb", "NoIncomingException", "ErrorMessageException"]

logger = logging.getLogger(__name__)


@dataclass
class Almabtrieb:
    """Implements the asynchronous API of the Cattle Drive Protocol"""

    connection: MqttConnection | AmqpConnection
    information: InformationResponse | None = None

    @property
    def connected(self):
        """Is one connected to the service"""
        return self.connection.connected

    def allowed_methods(self):
        """Returns the set of methods allowed by the connection"""
        if not self.connected:
            raise Exception("information property not set")

        if not self.information:
            raise Exception("information property not set")

        return [
            method.get("routing_key") for method in self.information.method_information
        ]

    @staticmethod
    def from_connection_string(
        connection_string: str, echo: bool = False, silent: bool = False
    ):
        """Creates instance for connection string

        ```python
        Almabtrieb.from_connection_string("ws://user:pass@host/ws")
        Almabtrieb.from_connection_string("amqp://user:pass@host/ws")
        ```

        :param connection_string: The connection string
        :param echo: Set to true to log all messages
        """

        params = ConnectionParams.from_string(connection_string)

        if params.protocol in ["ws", "wss", "mqtt"]:
            return Almabtrieb(
                connection=MqttConnection.from_connection_string(
                    connection_string, echo=echo, silent=silent
                )
            )
        elif params.protocol == "amqp":
            if params.username is None:
                raise ValueError("Username is required for connection")
            return Almabtrieb(
                connection=AmqpConnection(
                    connection_string=connection_string,
                    echo=echo,
                    username=params.username,
                    silent=silent,
                )
            )
        else:
            raise NotImplementedError("Protocol not implemented")

    async def run(self):
        """Starts the connection and queries for new received messages

        ```python
        task = asyncio.create_task(almabtrieb.run())
        ...
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        ```
        """
        try:
            await self.connection.run()
            logger.info("Run terminated")
        except Exception as e:
            logger.info("Ran into exception when running connection")
            logger.exception(e)

    async def info(self) -> InformationResponse:
        """Returns the information about the connected
        Cattle Drive server. The response is stored
        in  the `information` property.

        :returns: The information about the server
        """
        result = await self.connection.send_with_reply("request/info", {})

        self.information = InformationResponse.model_validate(result)
        return self.information

    async def create_actor(
        self,
        base_url: str,
        preferred_username: str | None = None,
        profile: dict = {},
        automatically_accept_followers: bool | None = None,
        name: str | None = None,
    ) -> dict:
        """Creates a new actor

        :param base_url: The base url of the actor
        :param preferred_username: The preferred username used as `acct:preferred_username@domain` where `domain` is from `base_url`
        :param profile: The profile of the actor
        :param automatically_accept_followers: If true, the server will automatically accept followers
        :param name: The internal name of the actor
        :returns: The created actor profile
        """
        request = CreateActorRequest(
            base_url=base_url,
            preferred_username=preferred_username,
            profile=profile,
            automatically_accept_followers=automatically_accept_followers,
            name=name,
        )

        return await self.connection.send_with_reply(
            "request/create_actor", request.model_dump()
        )

    async def fetch(self, actor: str, uri: str, timeout: float = 1) -> FetchResponse:
        """Fetches the object with uri `uri` as the actor with actor id `actor`.

        :param actor: The actor id must be part of actors from the info response
        :param uri: The uri of the object to fetch
        :param timeout: The timeout for the request
        :returns: The fetched object
        """
        async with asyncio.timeout(timeout):
            result = await self.connection.send_with_reply(
                "request/fetch", FetchMessage(actor=actor, uri=uri).model_dump()
            )

            return FetchResponse.model_validate(result)

    async def trigger(self, method: str, data: dict):
        """Triggers a method on the backend. Checks that method
        is contained in the methods from the information response.
        Allowed methods correspond to the routing_key property.deleter

        If the information property is not set, an info call is done."""
        end = f"trigger/{method}"

        if not self.information:
            await self.info()

        if method not in self.allowed_methods():
            raise ValueError(f"Method {method} is not supported by the backend")

        return await self.connection.send(
            end,
            data,
        )

    async def incoming(self):
        """Generator for the incoming messages"""
        while msg := await self.connection.incoming_queue.get():
            if msg is None:
                return
            yield msg

    async def outgoing(self):
        """Generator for the outgoing messages"""
        while msg := await self.connection.outgoing_queue.get():
            if msg is None:
                return
            yield msg

    async def next_incoming(self, timeout: float = 1) -> dict:
        """Returns the next incoming message

        :param timeout: The timeout for the request
        :returns: The next incoming message
        """
        try:
            async with asyncio.timeout(timeout):
                return await self.connection.incoming_queue.get()
        except asyncio.TimeoutError:
            raise NoIncomingException("No incoming message")

    async def next_outgoing(self, timeout: float = 1) -> dict:
        """Returns the next outgoing message

        :param timeout: The timeout for the request
        :returns: The next outgoing message
        """
        try:
            async with asyncio.timeout(timeout):
                return await self.connection.outgoing_queue.get()
        except asyncio.TimeoutError:
            raise NoIncomingException("No outgoing message")

    async def next_error(self, timeout: float = 1) -> dict:
        """Returns the next error message

        :param timeout: The timeout for the request
        :returns: The next error message
        """
        try:
            async with asyncio.timeout(timeout):
                return await self.connection.error_queue.get()
        except asyncio.TimeoutError:
            raise NoIncomingException("No error message")

    async def clear_incoming(self) -> None:
        """Empties the incoming message queue"""
        while not self.connection.incoming_queue.empty():
            await self.connection.incoming_queue.get()

    async def __aenter__(self):
        self.task = asyncio.create_task(self.run())
        while not self.connected:
            if self.task.done():
                raise ConnectionError("Could not connect to server")
            logger.info("Waiting for connection")
            await asyncio.sleep(0.5)

        await self.info()

    async def __aexit__(self, exc_type, exc, tb):
        self.task.cancel()
        try:
            await self.task
        except asyncio.CancelledError:
            pass


@asynccontextmanager
async def connect(
    connection_string: str, echo: bool = False, sleep_time: float = 0.5
) -> AsyncGenerator[Almabtrieb, None]:
    """Connects to the service

    Usage
    ```python
    async with connect("ws://user:pass@host/ws") as almabtrieb:
        print(await almabtrieb.info())
    ```

    :param connection_string: The connection string
    :param echo: Set to true to log all messages
    :param sleep_time: The time to wait between checking if connected
    """
    almabtrieb = Almabtrieb.from_connection_string(
        connection_string=connection_string,
        echo=echo,
    )

    task = asyncio.create_task(almabtrieb.run())
    while not almabtrieb.connected:
        if task.done():
            raise ConnectionError("Could not connect to server")
        logger.info("Waiting for connection")
        await asyncio.sleep(sleep_time)
    try:
        await almabtrieb.info()
        yield almabtrieb
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
