import time
import math
import asyncio
import logging
from . import msg
from .parse_error import ParseError

logger = logging.getLogger(__name__)


class Server(object):
    def __init__(self, name: str):
        self._name = name
        self._server = None
        self._listen_host = None
        self._listen_port = None
        self._running_server = None

    async def serve(self, handler):
        """
        Start TCP server
        :param handler: called for each new connection. async function
        :type handler: async lambda reader, writer -> None
        :return:
        """
        self._server = await asyncio.start_server(handler, host='0.0.0.0')

        self._listen_host, self._listen_port = self._server.sockets[0].getsockname()
        logger.info(f"Listening on {self._listen_port}:{self._listen_port}")

        self._running_server = asyncio.ensure_future(self._server_loop())

        return self._listen_host, self._listen_port

    async def _server_loop(self):
        async with self._server:
            await self._server.serve_forever()

    async def close(self):
        self._server.shutdown()
        await self._running_server

    @property
    def listen_host(self):
        assert self._server is not None
        return self._listen_host

    @property
    def listen_port(self):
        assert self._server is not None
        return self._listen_port


class Connection(object):
    """Manages a Gazebo protocol connection.
    """

    def __init__(self, name):
        self.name = name
        self._address = None
        self._port = None
        self._reader = None
        self._writer = None
        self._closed = True

    async def connect(self, address, port):
        logger.debug('Connection.connect')
        self._address = address
        self._port = port

        reader, writer = await asyncio.open_connection(address, port)
        self.accept_connection(reader, writer)

    def accept_connection(self, reader, writer):
        self._reader = reader
        self._writer = writer
        self._closed = False

    async def close(self):
        if self._closed:
            raise RuntimeError("Cannot closed an already closed connection")

        self._writer.close()
        await self._writer.wait_closed()

    async def write_packet(self, name: str, message):
        assert not self._closed
        packet = msg.packet_pb2.Packet()
        cur_time = time.time()
        packet.stamp.sec = int(cur_time)
        packet.stamp.nsec = int(math.fmod(cur_time, 1) * 1e9)
        packet.type = name.encode()
        packet.serialized_data = message.SerializeToString()
        await self._write(packet.SerializeToString())

    async def write(self, message):
        data = message.SerializeToString()
        await self._write(data)

    async def _write(self, data):
        header = ('%08X' % len(data)).encode()
        self._writer.write(header + data)
        await self._writer.drain()

    async def read_raw(self):
        """
        Read incoming packet without parsing it
        :return: byte array of the packet
        """
        assert not self._closed
        header = await self._reader.readexactly(8)
        if len(header) < 8:
            raise ParseError('malformed header: ' + str(header))

        try:
            size = int(header, 16)
        except ValueError:
            raise ParseError('invalid header: ' + str(header))
        else:
            data = await self._reader.readexactly(size)
            return data

    async def read_packet(self):
        data = await self.read_raw()
        packet = msg.packet_pb2.Packet.FromString(data)
        return packet

