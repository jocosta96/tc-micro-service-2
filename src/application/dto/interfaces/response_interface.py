from abc import ABC, abstractmethod
from typing import Any

class ResponseInterface(ABC):
    """Interface for response DTOs"""

    @abstractmethod
    def to_dict(self) -> dict:
        """Convert the response DTO to a dictionary"""
        pass

    @classmethod
    @abstractmethod
    def from_entity(cls, entity: Any) -> "ResponseInterface":
        """Create a response DTO from an entity"""
        pass
