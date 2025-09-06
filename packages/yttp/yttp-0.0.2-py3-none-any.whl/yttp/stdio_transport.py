import asyncio
import sys
import os
from typing import Optional
from .transport import Transport
from ybase.result import Result, Ok


class StdioTransport(Transport):
    """
    Transport implementation for stdio-based communication (LSP/MCP style).
    
    Reads from stdin and writes to stdout for process-to-process communication.
    """
    
    def __init__(self):
        self._stdin_reader: Optional[asyncio.StreamReader] = None
        self._stdout_writer: Optional[asyncio.StreamWriter] = None
        self._initialized = False
        self._buffer = b""
    
    async def _ensure_initialized(self) -> Result[None]:
        """Initialize asyncio streams if not already done"""
        if not self._initialized:
            try:
                loop = asyncio.get_event_loop()
                
                # Setup stdin reader
                self._stdin_reader = asyncio.StreamReader()
                await loop.connect_read_pipe(
                    lambda: asyncio.StreamReaderProtocol(self._stdin_reader), 
                    sys.stdin
                )
                
                # Setup stdout writer using FlowControlMixin
                writer_transport, writer_protocol = await loop.connect_write_pipe(
                    lambda: asyncio.streams.FlowControlMixin(),
                    os.fdopen(sys.stdout.fileno(), 'wb')
                )
                self._stdout_writer = asyncio.StreamWriter(writer_transport, writer_protocol, None, loop)
                
                self._initialized = True
                return Ok(None)
            except OSError as e:
                return Result.error("Failed to initialize stdio streams", e)
        return Ok(None)
    
    async def read(self, timeout: float = 1.0) -> Result[bytes]:
        """
        Read data from stdin with proper buffering for HTTP parser.
        """
        # If we have buffered data, return some of it
        if self._buffer:
            # Return up to 8192 bytes from buffer
            chunk_size = min(8192, len(self._buffer))
            data = self._buffer[:chunk_size]
            self._buffer = self._buffer[chunk_size:]
            return Ok(data)
        
        # No buffered data, read from stdin
        loop = asyncio.get_event_loop()
        
        def read_stdin():
            # Read all available data from stdin
            data = sys.stdin.buffer.read()
            return data
        
        try:
            data = await asyncio.wait_for(
                loop.run_in_executor(None, read_stdin),
                timeout=timeout
            )
            
            if not data:
                return Result.error("stdin closed")
            
            # Buffer the data and return first chunk
            self._buffer = data
            chunk_size = min(8192, len(self._buffer))
            result_data = self._buffer[:chunk_size]
            self._buffer = self._buffer[chunk_size:]
            
            return Ok(result_data)
            
        except asyncio.TimeoutError as e:
            return Result.error(f"stdin read timeout after {timeout}s", e)
        except OSError as e:
            return Result.error("stdin read error", e)
    
    async def write(self, data: bytes) -> Result[None]:
        """
        Write data to stdout using the StreamWriter.
        """
        init_result = await self._ensure_initialized()
        if init_result.is_err:
            return init_result
        
        try:
            self._stdout_writer.write(data)
            await self._stdout_writer.drain()
            return Ok(None)
        except OSError as e:
            return Result.error("stdout write error", e)
