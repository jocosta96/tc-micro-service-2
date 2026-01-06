"""
Comprehensive tests for SQLAlchemyDatabase to increase coverage.
Focuses on error handling, edge cases, and all CRUD operations.
"""
from unittest.mock import MagicMock, patch, PropertyMock
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.adapters.gateways.implementations.sqlalchemy_database import SQLAlchemyDatabase


class MockEntity:
    """Mock entity for testing"""
    internal_id = None  # Class attribute for filter queries
    
    def __init__(self, internal_id=None):
        self.internal_id = internal_id


def test_add_success():
    """Given valid entity, when add is called, then entity is added and flushed"""
    # Arrange
    db = SQLAlchemyDatabase(database_url="sqlite:///:memory:")
    mock_session = MagicMock(spec=Session)
    entity = MockEntity(internal_id=1)
    
    # Act
    result = db.add(mock_session, entity)
    
    # Assert
    mock_session.add.assert_called_once_with(entity)
    mock_session.flush.assert_called_once()
    assert result == entity


def test_add_with_sqlalchemy_error():
    """Given SQLAlchemy error on flush, when add is called, then ValueError is raised and rollback is called"""
    # Arrange
    db = SQLAlchemyDatabase(database_url="sqlite:///:memory:")
    mock_session = MagicMock(spec=Session)
    mock_session.flush.side_effect = SQLAlchemyError("Database error")
    entity = MockEntity()
    
    # Act & Assert
    try:
        db.add(mock_session, entity)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Error adding entity" in str(e)
        mock_session.rollback.assert_called_once()


def test_update_success():
    """Given valid entity, when update is called, then entity is merged and flushed"""
    # Arrange
    db = SQLAlchemyDatabase(database_url="sqlite:///:memory:")
    mock_session = MagicMock(spec=Session)
    entity = MockEntity(internal_id=1)
    mock_session.merge.return_value = entity
    
    # Act
    result = db.update(mock_session, entity)
    
    # Assert
    mock_session.merge.assert_called_once_with(entity)
    mock_session.flush.assert_called_once()
    assert result == entity


def test_update_with_sqlalchemy_error():
    """Given SQLAlchemy error on merge, when update is called, then ValueError is raised and rollback is called"""
    # Arrange
    db = SQLAlchemyDatabase(database_url="sqlite:///:memory:")
    mock_session = MagicMock(spec=Session)
    mock_session.merge.side_effect = SQLAlchemyError("Constraint violation")
    entity = MockEntity()
    
    # Act & Assert
    try:
        db.update(mock_session, entity)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Error updating entity" in str(e)
        mock_session.rollback.assert_called_once()


def test_delete_success():
    """Given valid entity, when delete is called, then entity is deleted and True is returned"""
    # Arrange
    db = SQLAlchemyDatabase(database_url="sqlite:///:memory:")
    mock_session = MagicMock(spec=Session)
    entity = MockEntity(internal_id=1)
    
    # Act
    result = db.delete(mock_session, entity)
    
    # Assert
    mock_session.delete.assert_called_once_with(entity)
    assert result is True


def test_delete_with_sqlalchemy_error():
    """Given SQLAlchemy error on delete, when delete is called, then ValueError is raised and rollback is called"""
    # Arrange
    db = SQLAlchemyDatabase(database_url="sqlite:///:memory:")
    mock_session = MagicMock(spec=Session)
    mock_session.delete.side_effect = SQLAlchemyError("Foreign key constraint")
    entity = MockEntity()
    
    # Act & Assert
    try:
        db.delete(mock_session, entity)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Error deleting entity" in str(e)
        mock_session.rollback.assert_called_once()


def test_find_by_id_found():
    """Given entity exists, when find_by_id is called, then entity is returned"""
    # Arrange
    db = SQLAlchemyDatabase(database_url="sqlite:///:memory:")
    mock_session = MagicMock(spec=Session)
    mock_query = MagicMock()
    mock_filter = MagicMock()
    entity = MockEntity(internal_id=1)
    
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_filter
    mock_filter.first.return_value = entity
    
    # Act
    result = db.find_by_id(mock_session, MockEntity, 1)
    
    # Assert
    assert result == entity
    mock_session.query.assert_called_once_with(MockEntity)


def test_find_by_id_not_found():
    """Given entity does not exist, when find_by_id is called, then None is returned"""
    # Arrange
    db = SQLAlchemyDatabase(database_url="sqlite:///:memory:")
    mock_session = MagicMock(spec=Session)
    mock_query = MagicMock()
    mock_filter = MagicMock()
    
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_filter
    mock_filter.first.return_value = None
    
    # Act
    result = db.find_by_id(mock_session, MockEntity, 999)
    
    # Assert
    assert result is None


def test_find_by_id_with_sqlalchemy_error():
    """Given SQLAlchemy error, when find_by_id is called, then ValueError is raised"""
    # Arrange
    db = SQLAlchemyDatabase(database_url="sqlite:///:memory:")
    mock_session = MagicMock(spec=Session)
    mock_session.query.side_effect = SQLAlchemyError("Connection error")
    
    # Act & Assert
    try:
        db.find_by_id(mock_session, MockEntity, 1)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Error finding entity by ID" in str(e)


def test_find_all_success():
    """Given entities exist, when find_all is called, then list of entities is returned"""
    # Arrange
    db = SQLAlchemyDatabase(database_url="sqlite:///:memory:")
    mock_session = MagicMock(spec=Session)
    mock_query = MagicMock()
    entities = [MockEntity(internal_id=1), MockEntity(internal_id=2)]
    
    mock_session.query.return_value = mock_query
    mock_query.all.return_value = entities
    
    # Act
    result = db.find_all(mock_session, MockEntity)
    
    # Assert
    assert result == entities
    assert len(result) == 2


def test_find_all_with_sqlalchemy_error():
    """Given SQLAlchemy error, when find_all is called, then ValueError is raised"""
    # Arrange
    db = SQLAlchemyDatabase(database_url="sqlite:///:memory:")
    mock_session = MagicMock(spec=Session)
    mock_session.query.side_effect = SQLAlchemyError("Query error")
    
    # Act & Assert
    try:
        db.find_all(mock_session, MockEntity)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Error finding all entities" in str(e)


def test_find_by_field_success():
    """Given valid field name, when find_by_field is called, then entity is returned"""
    # Arrange
    db = SQLAlchemyDatabase(database_url="sqlite:///:memory:")
    mock_session = MagicMock(spec=Session)
    mock_query = MagicMock()
    mock_filter = MagicMock()
    entity = MockEntity(internal_id=1)
    
    MockEntity.internal_id = PropertyMock(return_value=1)
    
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_filter
    mock_filter.first.return_value = entity
    
    # Act
    result = db.find_by_field(mock_session, MockEntity, "internal_id", 1)
    
    # Assert
    assert result == entity


def test_find_by_field_invalid_field_name():
    """Given invalid field name, when find_by_field is called, then ValueError is raised"""
    # Arrange
    db = SQLAlchemyDatabase(database_url="sqlite:///:memory:")
    mock_session = MagicMock(spec=Session)
    
    # Act & Assert
    try:
        db.find_by_field(mock_session, MockEntity, "nonexistent_field", "value")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Invalid field name 'nonexistent_field'" in str(e)


def test_find_by_field_with_sqlalchemy_error():
    """Given SQLAlchemy error, when find_by_field is called, then ValueError is raised"""
    # Arrange
    db = SQLAlchemyDatabase(database_url="sqlite:///:memory:")
    mock_session = MagicMock(spec=Session)
    
    MockEntity.internal_id = PropertyMock(return_value=1)
    mock_session.query.side_effect = SQLAlchemyError("Connection lost")
    
    # Act & Assert
    try:
        db.find_by_field(mock_session, MockEntity, "internal_id", 1)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Error finding entity by field" in str(e)


def test_find_all_by_field_multiple_results():
    """Given multiple entities match field, when find_all_by_field is called, then list is returned"""
    # Arrange
    db = SQLAlchemyDatabase(database_url="sqlite:///:memory:")
    mock_session = MagicMock(spec=Session)
    mock_query = MagicMock()
    mock_filter = MagicMock()
    entities = [MockEntity(internal_id=1), MockEntity(internal_id=2), MockEntity(internal_id=3)]
    
    MockEntity.status = PropertyMock(return_value="ACTIVE")
    
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_filter
    mock_filter.all.return_value = entities
    
    # Act
    result = db.find_all_by_field(mock_session, MockEntity, "status", "ACTIVE")
    
    # Assert
    assert result == entities
    assert len(result) == 3


def test_find_all_by_field_invalid_field():
    """Given invalid field name, when find_all_by_field is called, then ValueError is raised"""
    # Arrange
    db = SQLAlchemyDatabase(database_url="sqlite:///:memory:")
    mock_session = MagicMock(spec=Session)
    
    # Act & Assert
    try:
        db.find_all_by_field(mock_session, MockEntity, "invalid_field", "value")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Invalid field name 'invalid_field'" in str(e)


def test_find_all_by_boolean_field_success():
    """Given boolean field, when find_all_by_boolean_field is called, then matching entities returned"""
    # Arrange
    db = SQLAlchemyDatabase(database_url="sqlite:///:memory:")
    mock_session = MagicMock(spec=Session)
    mock_query = MagicMock()
    mock_filter = MagicMock()
    entities = [MockEntity(internal_id=1)]
    
    MockEntity.is_active = PropertyMock(return_value=True)
    
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_filter
    mock_filter.all.return_value = entities
    
    # Act
    result = db.find_all_by_boolean_field(mock_session, MockEntity, "is_active", True)
    
    # Assert
    assert result == entities


def test_find_all_by_multiple_fields_success():
    """Given multiple field filters, when find_all_by_multiple_fields is called, then filtered entities returned"""
    # Arrange
    db = SQLAlchemyDatabase(database_url="sqlite:///:memory:")
    mock_session = MagicMock(spec=Session)
    mock_query = MagicMock()
    entities = [MockEntity(internal_id=1)]
    
    MockEntity.status = PropertyMock(return_value="ACTIVE")
    MockEntity.category = PropertyMock(return_value="VIP")
    
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query  # Chain filters
    mock_query.all.return_value = entities
    
    # Act
    result = db.find_all_by_multiple_fields(mock_session, MockEntity, {"status": "ACTIVE", "category": "VIP"})
    
    # Assert
    assert result == entities


def test_exists_by_field_true():
    """Given entity exists with field value, when exists_by_field is called, then True is returned"""
    # Arrange
    db = SQLAlchemyDatabase(database_url="sqlite:///:memory:")
    mock_session = MagicMock(spec=Session)
    mock_query = MagicMock()
    mock_filter = MagicMock()
    
    MockEntity.email = PropertyMock(return_value="test@test.com")
    
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_filter
    mock_filter.first.return_value = MockEntity()
    
    # Act
    result = db.exists_by_field(mock_session, MockEntity, "email", "test@test.com")
    
    # Assert
    assert result is True


def test_exists_by_field_false():
    """Given entity does not exist, when exists_by_field is called, then False is returned"""
    # Arrange
    db = SQLAlchemyDatabase(database_url="sqlite:///:memory:")
    mock_session = MagicMock(spec=Session)
    mock_query = MagicMock()
    mock_filter = MagicMock()
    
    MockEntity.email = PropertyMock(return_value="test@test.com")
    
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_filter
    mock_filter.first.return_value = None
    
    # Act
    result = db.exists_by_field(mock_session, MockEntity, "email", "nonexistent@test.com")
    
    # Assert
    assert result is False


def test_commit_success():
    """Given valid session, when commit is called, then session is committed"""
    # Arrange
    db = SQLAlchemyDatabase(database_url="sqlite:///:memory:")
    mock_session = MagicMock(spec=Session)
    
    # Act
    db.commit(mock_session)
    
    # Assert
    mock_session.commit.assert_called_once()


def test_commit_with_error():
    """Given commit error, when commit is called, then ValueError is raised and rollback is called"""
    # Arrange
    db = SQLAlchemyDatabase(database_url="sqlite:///:memory:")
    mock_session = MagicMock(spec=Session)
    mock_session.commit.side_effect = SQLAlchemyError("Commit failed")
    
    # Act & Assert
    try:
        db.commit(mock_session)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Error committing transaction" in str(e)
        mock_session.rollback.assert_called_once()


def test_rollback_success():
    """Given valid session, when rollback is called, then session is rolled back"""
    # Arrange
    db = SQLAlchemyDatabase(database_url="sqlite:///:memory:")
    mock_session = MagicMock(spec=Session)
    
    # Act
    db.rollback(mock_session)
    
    # Assert
    mock_session.rollback.assert_called_once()


def test_rollback_with_error():
    """Given rollback error, when rollback is called, then ValueError is raised"""
    # Arrange
    db = SQLAlchemyDatabase(database_url="sqlite:///:memory:")
    mock_session = MagicMock(spec=Session)
    mock_session.rollback.side_effect = SQLAlchemyError("Rollback failed")
    
    # Act & Assert
    try:
        db.rollback(mock_session)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Error rolling back transaction" in str(e)


def test_close_session_success():
    """Given valid session, when close_session is called, then session is closed"""
    # Arrange
    db = SQLAlchemyDatabase(database_url="sqlite:///:memory:")
    mock_session = MagicMock(spec=Session)
    
    # Act
    db.close_session(mock_session)
    
    # Assert
    mock_session.close.assert_called_once()


def test_close_session_with_error():
    """Given close error, when close_session is called, then ValueError is raised"""
    # Arrange
    db = SQLAlchemyDatabase(database_url="sqlite:///:memory:")
    mock_session = MagicMock(spec=Session)
    mock_session.close.side_effect = SQLAlchemyError("Close failed")
    
    # Act & Assert
    try:
        db.close_session(mock_session)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Error closing session" in str(e)


def test_get_session_returns_session():
    """Given database instance, when get_session is called, then Session instance is returned"""
    # Arrange
    db = SQLAlchemyDatabase(database_url="sqlite:///:memory:")
    
    # Act
    session = db.get_session()
    
    # Assert
    assert session is not None
    assert isinstance(session, Session)
