from abc import ABC, abstractmethod
from typing import List, Optional


from src.entities.order import Order


class OrderRepository(ABC):
    """
    Abstract interface for Order repository operations.
    
    This interface defines the contract for order data access operations
    without specifying the implementation details.
    """

    @abstractmethod
    def create(self, order: Order) -> Order:
        """Create a new order"""
        pass

    @abstractmethod
    def get_by_id(self, order_internal_id: int) -> Optional[Order]:
        """Get order by ID"""
        pass



    @abstractmethod
    def get_by_status(self, status: str) -> List[Order]:
        """Get all orders with a specific status"""
        pass

    @abstractmethod
    def list_all(self, skip: int = 0, limit: int = 100) -> List[Order]:
        """List all orders with pagination"""
        pass

    @abstractmethod
    def update(self, order: Order) -> Order:
        """Update an existing order"""
        pass

    @abstractmethod
    def cancel(self, order_internal_id: int) -> bool:
        """Cancel an order by ID"""
        pass

    @abstractmethod
    def update_status(self, order_internal_id: int, status: str) -> Optional[Order]:
        """Update order status"""
        pass

    @abstractmethod
    def process_payment(self, order_internal_id: int, payment_data: dict) -> Optional[Order]:
        """Process payment for an order"""
        pass

    @abstractmethod
    def get_payment_status(self, order_internal_id: int) -> Optional[dict]:
        """Get payment status for an order"""
        pass 