from abc import ABC, abstractmethod
from typing import TypeVar, Any

T = TypeVar("T")


class PresenterInterface(ABC):
    """
    Presenter interface that defines the contract for data presentation.

    In Clean Architecture:
    - This is part of the Interface Adapters layer
    - It handles the formatting of data for different output formats
    - It converts domain entities/DTOs to presentation format
    - It keeps the application layer independent of presentation concerns
    """

    @abstractmethod
    def present(self, data: Any) -> dict:
        """Present data in the required format"""
        pass

    @abstractmethod
    def present_list(self, data_list: list) -> dict:
        """Present a list of data in the required format"""
        pass

    @abstractmethod
    def present_error(self, error: Exception) -> dict:
        """Present error information in the required format"""
        pass
