from urllib.parse import urlparse
from dataclasses import dataclass

import re


@dataclass
class ConnectionParams:
    protocol: str
    host: str
    port: int
    username: str | None = None
    password: str | None = None
    path: str | None = None

    @staticmethod
    def from_string(connection_string: str):
        """
        ```pycon
        >>> ConnectionParams.from_string("ws://user:pass@host/ws")
        ConnectionParams(protocol='ws', host='host', port=80, username='user', password='pass', path='/ws')

        ```
        """
        parsed = parse_connection_string(connection_string)

        return ConnectionParams(**parsed)


def parse_connection_string(connection_string: str) -> dict:
    """
    Parse a connection string into a dictionary of connection parameters.

    ```pycon
    >>> parse_connection_string("ws://user:pass@host/ws")
    {'host': 'host',
        'port': 80,
        'protocol': 'ws',
        'username': 'user',
        'password': 'pass',
        'path': '/ws'}

    >>> parse_connection_string("wss://user:pass@host/ws")
    {'host': 'host',
        'port': 443,
        'protocol': 'wss',
        'username': 'user',
        'password': 'pass',
        'path': '/ws'}

    ```
    """

    parsed = urlparse(connection_string)

    default_port = 80 if parsed.scheme == "ws" else 443

    return {
        "host": parsed.hostname,
        "port": parsed.port or default_port,
        "protocol": parsed.scheme,
        "username": parsed.username,
        "password": parsed.password,
        "path": parsed.path,
    }


def censor_password(connection_string: str) -> str:
    """
    Censor the password in a connection string.

    ```pycon
    >>> censor_password("ws://user:pass@host/ws")
    'ws://user:***@host/ws'

    ```
    """

    return re.sub(r":[^/]*?@", ":***@", connection_string)
