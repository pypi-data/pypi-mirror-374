from .transport import Transport
from ybase.result import Result, Ok
from .http import Message
from .http_parser import Connection, Request, Headers, Data, EndOfMessage, NEED_DATA

class Reader:
    """
    Parses complete HTTP-style messages from a transport.
    """
    def __init__(self, transport: Transport):
        self.transport = transport
        self.conn = Connection("server")

    async def next_message(self, timeout: float = 1.0) -> Result[Message]:
        """
        Reads and parses a complete message from the transport.

        Args:
            timeout: The maximum time in seconds to wait for data for each read.
                     Defaults to 1 second.

        Returns:
            A Result containing the parsed Message on success, or an error.
        """
        headers = None
        body_parts = []

        while True:
            event_result = self.conn.next_event()
            if not event_result:
                return Result.error("Parser error", event_result)
            
            event = event_result.unwrapped

            if event is NEED_DATA:
                read_result = await self.transport.read(timeout=timeout)
                if read_result.is_err:
                    return Result.error("Transport read error", read_result.error)
                
                data = read_result.unwrapped
                self.conn.receive_data(data)
                continue

            if isinstance(event, Request):
                if headers is not None:
                    return Result.error("Unexpected Request event: message already started")
                headers = event.headers
            elif isinstance(event, Headers):
                if headers is not None:
                    return Result.error("Unexpected Headers event: message already started")
                headers = event.headers
            elif isinstance(event, Data):
                if headers is None:
                    return Result.error("Unexpected Data event: message not started")
                body_parts.append(event.data)
            elif isinstance(event, EndOfMessage):
                if headers is None:
                    return Result.error("Unexpected EndOfMessage event: message not started")
                full_body = b''.join(body_parts)
                return Ok(Message(headers=headers, body=full_body))
            else:
                return Result.error(f"Unexpected event: {type(event).__name__}")
