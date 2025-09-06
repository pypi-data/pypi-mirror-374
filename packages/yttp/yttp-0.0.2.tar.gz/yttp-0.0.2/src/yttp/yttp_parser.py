"""
Event-driven, LSP-style HTTP parser.

This module provides a simple, event-driven parser for protocols that use an
HTTP-like header block for message framing, such as the Language Server Protocol (LSP).

The parser is designed to be fed bytes incrementally and emits events as they
are parsed.

Key Features:
- No exceptions are raised. All methods return a Result[T].
- `Content-Length` header is mandatory.
- All headers are parsed and returned; none are ignored.
- Header order is not significant for parsing logic.

State Machine:
- WANT_HEADERS: Waiting for the full header block.
- WANT_BODY: Waiting for the message body.
- COMPLETE: The message has been fully parsed.
- ERROR: A fatal error occurred.
"""

from enum import Enum
from typing import List, Tuple, Union, Optional
from dataclasses import dataclass

# Assuming ybase.result is in the path
from ybase.result import Result, Ok

# --- Public API ---

class State(Enum):
    """Current state of the parser."""
    WANT_HEADERS = "want_headers"
    WANT_BODY = "want_body"
    COMPLETE = "complete"
    ERROR = "error"

@dataclass(frozen=True)
class Headers:
    """
    Emitted when headers are successfully parsed.
    
    Attributes:
        headers: A list of (name, value) tuples for all headers found.
    """
    headers: List[Tuple[bytes, bytes]]

@dataclass(frozen=True)
class Data:
    """Emitted when a chunk of the message body is available."""
    data: bytes

@dataclass(frozen=True)
class EndOfMessage:
    """Emitted when the message is completely parsed."""
    pass

class _NeedData:
    """Sentinel class indicating the parser needs more data."""
    pass

NEED_DATA = _NeedData()

Event = Union[Headers, Data, EndOfMessage, _NeedData]

class Connection:
    """
    An LSP-style parser object.
    
    Feed this object bytes using `receive_data()`, and then call `next_event()`
    to get a stream of parsing events.
    """
    
    def __init__(self):
        self._state = State.WANT_HEADERS
        self._buffer = b""
        self._content_length: Optional[int] = None
        self._body_bytes_read = 0
        self._event_queue: List[Event] = []
        self._error: Optional[Result] = None

    @property
    def state(self) -> State:
        """The current state of the parser."""
        return self._state

    def receive_data(self, data: bytes) -> None:
        """
        Feed new data into the parser.
        
        Args:
            data: The bytes received from the transport.
        """
        if self._state in {State.ERROR, State.COMPLETE}:
            return
        self._buffer += data

    def next_event(self) -> Result[Event]:
        """
        Get the next parsing event.
        
        Returns:
            A `Result` which is `Ok(Event)` on success or `Err(str)` on failure.
            If more data is needed, returns `Ok(NEED_DATA)`.
        """
        if self._event_queue:
            return Ok(self._event_queue.pop(0))

        if self._state == State.ERROR:
            return Result.error("Parser is in an error state", self._error)
        if self._state == State.COMPLETE:
            return Result.error("Parsing is complete.")

        # Try to parse more data and fill the event queue
        self._run_parser()

        if self._state == State.ERROR:
            return Result.error("Parser is in an error state", self._error)

        if self._event_queue:
            return Ok(self._event_queue.pop(0))
        
        # If we're here, we need more data
        return Ok(NEED_DATA)

    def _run_parser(self) -> None:
        if self._state == State.WANT_HEADERS:
            self._parse_headers()
        elif self._state == State.WANT_BODY:
            self._parse_body()

    def _parse_headers(self) -> None:
        separator = b'\r\n\r\n'
        if separator not in self._buffer:
            return
            
        header_bytes, self._buffer = self._buffer.split(separator, 1)
        
        headers: List[Tuple[bytes, bytes]] = []
        content_length: Optional[int] = None
        
        lines = header_bytes.split(b'\r\n')
        for line in lines:
            if not line:
                continue
                
            if b':' not in line:
                self._set_error(f"Invalid header line: {line.decode('utf-8', 'ignore')}")
                return
            
            name, value = line.split(b':', 1)
            name = name.strip().lower()
            value = value.strip()
            headers.append((name, value))
            
            if name.lower() == b'content-length':
                try:
                    content_length = int(value)
                except ValueError:
                    self._set_error(f"Invalid Content-Length value: {value.decode('utf-8', 'ignore')}")
                    return

        if content_length is None:
            self._set_error("Mandatory Content-Length header is missing.")
            return
            
        self._content_length = content_length
        self._event_queue.append(Headers(headers=headers))
        
        if self._content_length == 0:
            self._event_queue.append(EndOfMessage())
            self._state = State.COMPLETE
        else:
            self._state = State.WANT_BODY

    def _parse_body(self) -> None:
        if self._content_length is None or len(self._buffer) == 0:
            return

        remaining = self._content_length - self._body_bytes_read
        data_to_emit = self._buffer[:remaining]
        self._buffer = self._buffer[len(data_to_emit):]
        self._body_bytes_read += len(data_to_emit)
        
        if data_to_emit:
            self._event_queue.append(Data(data=data_to_emit))
        
        if self._body_bytes_read == self._content_length:
            self._event_queue.append(EndOfMessage())
            self._state = State.COMPLETE

    def _set_error(self, message: str) -> None:
        self._state = State.ERROR
        self._error = Result.error(message)
        self._event_queue.clear()