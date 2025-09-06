
from abc import ABC, abstractmethod
from ybase.result import Result

class Transport(ABC):
    """
    An abstract base class for a transport layer that can read and write bytes asynchronously.
    """

    @abstractmethod
    async def read(self, timeout: float = 1.0) -> Result[bytes]:
        """
        Reads data from the transport.

        Args:
            timeout: The maximum time in seconds to wait for data. Defaults to 1 second.

        Returns:
            Result containing the bytes read from the transport, or error.
        """
        pass

    @abstractmethod
    async def write(self, data: bytes) -> Result[bool]:
        """
        Writes data to the transport.

        Args:
            data: The bytes to write.
            
        Returns:
            Result indicating success or error.
        """
        pass
