from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Dict, Any
from sqlalchemy.orm import Session

T = TypeVar("T")


class DatabaseInterface(ABC):
    """
    Database interface that abstracts ORM operations.

    In Clean Architecture:
    - This is part of the Interface Adapters layer
    - It defines the contract for database operations
    - It's implemented by concrete database adapters
    - It keeps the repository independent of specific ORM details
    """

    @abstractmethod
    def get_session(self) -> Session:
        """Get a database session"""
        pass

    @abstractmethod
    def add(self, session: Session, entity: T) -> T:
        """Add an entity to the session"""
        pass

    @abstractmethod
    def update(self, session: Session, entity: T) -> T:
        """Update an entity in the session"""
        pass

    @abstractmethod
    def delete(self, session: Session, entity: T) -> bool:
        """Delete an entity from the session"""
        pass

    @abstractmethod
    def find_by_id(
        self, session: Session, entity_class: type, entity_id: int
    ) -> Optional[T]:
        """Find an entity by ID"""
        pass

    @abstractmethod
    def find_all(self, session: Session, entity_class: type) -> List[T]:
        """Find all entities of a given class"""
        pass

    @abstractmethod
    def find_by_field(
        self, session: Session, entity_class: type, field_name: str, field_value: any
    ) -> Optional[T]:
        """Find an entity by a specific field value"""
        pass

    @abstractmethod
    def find_all_by_field(
        self, session: Session, entity_class: type, field_name: str, field_value: any
    ) -> List[T]:
        """Find all entities by a specific field value"""
        pass

    @abstractmethod
    def find_all_by_boolean_field(
        self, session: Session, entity_class: type, field_name: str, field_value: bool
    ) -> List[T]:
        """Find all entities by a boolean field value"""
        pass

    @abstractmethod
    def find_all_by_multiple_fields(
        self, session: Session, entity_class: type, field_values: Dict[str, Any]
    ) -> List[T]:
        """Find all entities by multiple field values"""
        pass

    @abstractmethod
    def exists_by_field(
        self, session: Session, entity_class: type, field_name: str, field_value: any
    ) -> bool:
        """Check if an entity exists by a specific field value"""
        pass

    @abstractmethod
    def commit(self, session: Session) -> None:
        """Commit the session"""
        pass

    @abstractmethod
    def rollback(self, session: Session) -> None:
        """Rollback the session"""
        pass

    @abstractmethod
    def close_session(self, session: Session) -> None:
        """Close the session"""
        pass
