from abc import ABC, abstractmethod

class RequestInterface(ABC):
    """Interface for request DTOs"""

    @abstractmethod
    def to_dict(self) -> dict:
        """Convert the request DTO to a dictionary"""
        pass