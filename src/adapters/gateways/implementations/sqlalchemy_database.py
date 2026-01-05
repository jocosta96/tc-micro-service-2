from typing import List, Optional, TypeVar, Dict, Any
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

from src.adapters.gateways.interfaces.database_interface import DatabaseInterface
from src.config.database import db_config

T = TypeVar("T")


class SQLAlchemyDatabase(DatabaseInterface):
    """
    SQLAlchemy implementation of DatabaseInterface.

    In Clean Architecture:
    - This is part of the Interface Adapters layer
    - It implements the database interface using SQLAlchemy
    - It handles all ORM-specific operations
    - It provides a clean abstraction for database operations
    """

    def __init__(self, database_url: str = None):
        if database_url is None:
            database_url = db_config.connection_string

        # Create engine with PostgreSQL-specific settings
        self.engine = create_engine(
            database_url, pool_pre_ping=True, pool_recycle=300, echo=False
        )

        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    def get_session(self) -> Session:
        """Get a database session"""
        return self.SessionLocal()

    def add(self, session: Session, entity: T) -> T:
        """Add an entity to the session"""
        try:
            session.add(entity)
            session.flush()  # Flush to get the ID
            return entity
        except SQLAlchemyError as e:
            session.rollback()
            raise ValueError(f"Error adding entity: {e}")

    def update(self, session: Session, entity: T) -> T:
        """Update an entity in the session"""
        try:
            session.merge(entity)
            session.flush()
            return entity
        except SQLAlchemyError as e:
            session.rollback()
            raise ValueError(f"Error updating entity: {e}")

    def delete(self, session: Session, entity: T) -> bool:
        """Delete an entity from the session"""
        try:
            session.delete(entity)
            return True
        except SQLAlchemyError as e:
            session.rollback()
            raise ValueError(f"Error deleting entity: {e}")

    def find_by_id(
        self, session: Session, entity_class: type, entity_id: int
    ) -> Optional[T]:
        """Find an entity by ID"""
        try:
            return (
                session.query(entity_class).filter(entity_class.internal_id == entity_id).first()
            )
        except SQLAlchemyError as e:
            raise ValueError(f"Error finding entity by ID: {e}")

    def find_all(self, session: Session, entity_class: type) -> List[T]:
        """Find all entities of a given class"""
        try:
            return session.query(entity_class).all()
        except SQLAlchemyError as e:
            raise ValueError(f"Error finding all entities: {e}")

    def find_by_field(
        self, session: Session, entity_class: type, field_name: str, field_value: any
    ) -> Optional[T]:
        """Find an entity by a specific field value"""
        try:
            field = getattr(entity_class, field_name)
            return session.query(entity_class).filter(field == field_value).first()
        except SQLAlchemyError as e:
            raise ValueError(f"Error finding entity by field: {e}")
        except AttributeError as e:
            raise ValueError(f"Invalid field name '{field_name}': {e}")

    def find_all_by_field(
        self, session: Session, entity_class: type, field_name: str, field_value: any
    ) -> List[T]:
        """Find all entities by a specific field value"""
        try:
            field = getattr(entity_class, field_name)
            return session.query(entity_class).filter(field == field_value).all()
        except SQLAlchemyError as e:
            raise ValueError(f"Error finding entities by field: {e}")
        except AttributeError as e:
            raise ValueError(f"Invalid field name '{field_name}': {e}")

    def find_all_by_boolean_field(
        self, session: Session, entity_class: type, field_name: str, field_value: bool
    ) -> List[T]:
        """Find all entities by a boolean field value"""
        try:
            field = getattr(entity_class, field_name)
            return session.query(entity_class).filter(field == field_value).all()
        except SQLAlchemyError as e:
            raise ValueError(f"Error finding entities by boolean field: {e}")
        except AttributeError as e:
            raise ValueError(f"Invalid field name '{field_name}': {e}")

    def find_all_by_multiple_fields(
        self, session: Session, entity_class: type, field_values: Dict[str, Any]
    ) -> List[T]:
        """Find all entities by multiple field values"""
        try:
            query = session.query(entity_class)
            for field_name, field_value in field_values.items():
                field = getattr(entity_class, field_name)
                query = query.filter(field == field_value)
            return query.all()
        except SQLAlchemyError as e:
            raise ValueError(f"Error finding entities by multiple fields: {e}")
        except AttributeError as e:
            raise ValueError(f"Invalid field name in {field_values}: {e}")

    def exists_by_field(
        self, session: Session, entity_class: type, field_name: str, field_value: any
    ) -> bool:
        """Check if an entity exists by a specific field value"""
        try:
            field = getattr(entity_class, field_name)
            return (
                session.query(entity_class).filter(field == field_value).first()
                is not None
            )
        except SQLAlchemyError as e:
            raise ValueError(f"Error checking entity existence: {e}")
        except AttributeError as e:
            raise ValueError(f"Invalid field name '{field_name}': {e}")

    def commit(self, session: Session) -> None:
        """Commit the session"""
        try:
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise ValueError(f"Error committing transaction: {e}")

    def rollback(self, session: Session) -> None:
        """Rollback the session"""
        try:
            session.rollback()
        except SQLAlchemyError as e:
            raise ValueError(f"Error rolling back transaction: {e}")

    def close_session(self, session: Session) -> None:
        """Close the session"""
        try:
            session.close()
        except SQLAlchemyError as e:
            raise ValueError(f"Error closing session: {e}")


