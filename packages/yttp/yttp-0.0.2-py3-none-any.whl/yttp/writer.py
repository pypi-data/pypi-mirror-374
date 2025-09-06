import h11
from .transport import Transport
from ybase.result import Result, Ok

class Writer:
    """
    Serializes h11 events to be sent to a peer over a transport.
    """
    def __init__(self, transport: Transport):
        self.transport = transport
        self.conn = h11.Connection(h11.CLIENT)

    async def send(self, event) -> Result[bool]:
        """
        Serializes an h11 event and sends the resulting bytes to the peer
        via the transport.

        Args:
            event: The h11 event to serialize and send.
        """
        try:
            data = self.conn.send(event)
        except h11.LocalProtocolError as e:
            return Result.error("H11 protocol error during serialization", e)

        if data is None:
            return Ok(True)

        try:
            await self.transport.write(data)
            return Ok(True)
        except OSError as e:
            return Result.error("Transport write error", e)
