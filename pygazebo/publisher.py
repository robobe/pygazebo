import asyncio
import logging
from . import DEBUG_LEVEL
logger = logging.getLogger(__name__)
logger.setLevel(DEBUG_LEVEL)


class PublisherRecord(object):
    """Information about a remote topic.

    :ivar topic: (str) the string description of the topic
    :ivar msg_type: (str) the Gazebo message type string
    :ivar host: (str) the remote host of the topic publisher
    :ivar port: (int) the remote port of the topic publisher
    """
    def __init__(self, msg):
        self.topic = msg.topic
        self.msg_type = msg.msg_type
        self.host = msg.host
        self.port = msg.port

    def __str__(self):
        return f'{self.topic} {self.msg_type} {self.host}:{self.port}'

    __repr__ = __str__

    def __hash__(self):
        return hash(f'{self.topic}:{self.host}:{self.port}')

    def __eq__(self, other):
        return hash(self) == hash(other)


class Publisher(object):
    """Publishes data to the Gazebo publish-subscribe bus.

    :ivar topic: (string) the topic name this publisher is using
    :ivar msg_type: (string) the Gazebo message type
    """
    def __init__(self, topic: str, msg_type):
        """:class:`Publisher` should not be directly created"""
        self._topic = topic
        self._msg_type = msg_type
        self._stop_connection = False
        self._listeners = []
        self._first_listener_promise = asyncio.Future()

    async def publish(self, message, timeout=60):
        """Publish a new instance of this data.

        :param timeout: timeout for the network request
        :param message: the message to publish
        :type message: :class:`google.protobuf.Message` instance
        """
        assert not self._stop_connection
        futures = []

        # Try writing to each of our listeners.  If any give an error,
        # disconnect them.
        for connection in self._listeners:
            future = connection.write(message, timeout=timeout)
            futures.append((future, connection))

        for future, connection in futures:
            try:
                print(f'PUBLISHER AWAIT FUTURE {future}')
                await future
            except Exception as e:
                import sys
                import traceback
                print(f'write error, closing connection:{e}', file=sys.stderr)
                traceback.print_exc()
                logger.debug(f'write error, closing connection:{e}')
                if connection in self._listeners:
                    self._listeners.remove(connection)
                    connection.close()
            except asyncio.TimeoutError as e:
                logger.debug(f'write timeout, closing connection:{e}')
                if connection in self._listeners:
                    self._listeners.remove(connection)
                    await connection.close()

    async def remove(self):
        """Stop advertising this topic.

        Note: Once :func:`remove` is called, no further methods should
        be called.
        """
        self._stop_connection = True
        for conn in self._listeners:
            await conn.close()

    def add_listener(self, connection):
        """
        Adds a connection to the list of subscriber of this topic

        :param connection: connection of the subscriber to this topic
        :type connection: connection.Connection
        :return:
        """
        assert not self._stop_connection
        self._listeners.append(connection)
        if not self._first_listener_promise.done():
            self._first_listener_promise.set_result(connection)

    def wait_for_listener(self):
        return self._first_listener_promise

    @property
    def msg_type(self):
        return self._msg_type
