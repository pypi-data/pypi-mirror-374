
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class Message:
    """
    Represents a complete message with headers and a body.
    """
    headers: List[Tuple[bytes, bytes]]
    body: bytes
