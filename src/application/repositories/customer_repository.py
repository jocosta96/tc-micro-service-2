from abc import ABC, abstractmethod
from typing import List, Optional
from src.entities.customer import Customer


class CustomerRepository(ABC):
    """
    Repository interface for Customer entity.

    In Clean Architecture:
    - This is part of the Application Business Rules layer
    - It defines the contract for customer data access
    - It's implemented by Interface Adapters layer
    - It's used by Use Cases in the Application layer
    """

    @abstractmethod
    def save(self, customer: Customer) -> Customer:
        """Save a customer and return the saved customer with ID"""
        pass

    @abstractmethod
    def find_by_id(self, customer_internal_id: int, include_inactive: bool = False) -> Optional[Customer]:
        """Find a customer by internal ID"""
        pass

    @abstractmethod
    def find_by_document(self, document: str, include_inactive: bool = False) -> Optional[Customer]:
        """Find a customer by document number"""
        pass

    @abstractmethod
    def find_by_email(self, email: str, include_inactive: bool = False) -> Optional[Customer]:
        """Find a customer by email"""
        pass

    @abstractmethod
    def find_all(self, include_inactive: bool = False) -> List[Customer]:
        """Find all customers"""
        pass

    @abstractmethod
    def delete(self, customer_internal_id: int) -> bool:
        """Soft delete a customer by internal ID (set is_active to False), return True if deleted"""
        pass

    @abstractmethod
    def get_anonymous_customer(self) -> Customer:
        """Get or create the anonymous customer"""
        pass

    @abstractmethod
    def exists_by_document(self, document: str, include_inactive: bool = False) -> bool:
        """Check if a customer exists with the given document"""
        pass

    @abstractmethod
    def exists_by_email(self, email: str, include_inactive: bool = False) -> bool:
        """Check if a customer exists with the given email"""
        pass
