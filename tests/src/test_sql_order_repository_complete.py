"""
Comprehensive tests for SQLOrderRepository to increase coverage.
Focuses on get_by_id, list_all, update, cancel, update_status, process_payment, find_by_status.
"""
from unittest.mock import MagicMock, patch, PropertyMock
from datetime import datetime

from src.adapters.gateways.sql_order_repository import SQLOrderRepository, OrderModel, OrderItemModel
from src.entities.order import Order, OrderItem
from src.entities.product import Product, ProductCategory
from src.entities.ingredient import Ingredient, IngredientType
from src.entities.value_objects.money import Money
from src.entities.value_objects.order_status import OrderStatus, OrderStatusType
from src.entities.value_objects.name import Name
from src.entities.value_objects.sku import SKU
from src.entities.value_objects.document import Document
from src.entities.value_objects.email import Email


def create_mock_order_model(internal_id=1, status="RECEBIDO"):
    """Factory to create OrderModel mock"""
    order_model = MagicMock(spec=OrderModel)
    order_model.internal_id = internal_id
    order_model.customer_internal_id = 1
    order_model.value = 50.0
    order_model.status = status
    order_model.start_date = datetime.now()
    order_model.end_date = None
    order_model.has_payment_verified = False
    order_model.payment_date = None
    order_model.payment_transaction_id = None
    order_model.payment_message = None
    order_model.order_display_id = "001"
    
    # Create mock order item
    item_model = MagicMock(spec=OrderItemModel)
    item_model.internal_id = 1
    item_model.product_internal_id = 1
    item_model.additional_ingredient_internal_ids = []
    item_model.remove_ingredient_internal_ids = []
    item_model.item_receipt = []
    item_model.price = 50.0
    
    order_model.order_items = [item_model]
    return order_model


def create_mock_product(internal_id=1):
    """Factory to create Product entity"""
    from src.entities.product import ProductReceiptItem
    
    # Create ingredient for product
    ingredient = create_mock_ingredient(internal_id=1)
    
    return Product(
        name=Name.create("Test Product"),
        price=Money(amount=10.0),
        is_active=True,
        default_ingredient=[ProductReceiptItem(ingredient, 1)],  # At least one ingredient required
        category=ProductCategory.BURGER,
        sku=SKU.create("P-1234-ABC"),  # Valid SKU format: Letter-4digits-3letters
        internal_id=internal_id
    )


def create_mock_ingredient(internal_id=1):
    """Factory to create Ingredient entity"""
    return Ingredient(
        name=Name.create("Test Ingredient"),
        price=Money(amount=2.0),
        is_active=True,
        type=IngredientType.CHEESE,  # Use 'type' not 'ingredient_type'
        applies_to_burger=True,
        applies_to_side=False,
        applies_to_drink=False,
        applies_to_dessert=False,
        internal_id=internal_id
    )


def test_get_by_id_found():
    """Given order exists, when get_by_id is called, then Order entity is returned"""
    # Arrange
    mock_db = MagicMock()
    mock_session = MagicMock()
    mock_db.get_session.return_value.__enter__.return_value = mock_session
    
    mock_product_repo = MagicMock()
    mock_ingredient_repo = MagicMock()
    
    order_model = create_mock_order_model(internal_id=1)
    
    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_filter
    mock_filter.first.return_value = order_model
    
    mock_product_repo.find_by_id.return_value = create_mock_product()
    
    repo = SQLOrderRepository(mock_db, mock_product_repo, mock_ingredient_repo)
    
    # Act
    result = repo.get_by_id(1)
    
    # Assert
    assert result is not None
    assert result.internal_id == 1
    mock_session.query.assert_called_once()


def test_get_by_id_not_found():
    """Given order does not exist, when get_by_id is called, then None is returned"""
    # Arrange
    mock_db = MagicMock()
    mock_session = MagicMock()
    mock_db.get_session.return_value.__enter__.return_value = mock_session
    
    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_filter
    mock_filter.first.return_value = None
    
    repo = SQLOrderRepository(mock_db)
    
    # Act
    result = repo.get_by_id(999)
    
    # Assert
    assert result is None


def test_list_all_with_pagination():
    """Given multiple orders exist, when list_all is called with skip/limit, then paginated list is returned"""
    # Arrange
    mock_db = MagicMock()
    mock_session = MagicMock()
    mock_db.get_session.return_value.__enter__.return_value = mock_session
    
    mock_product_repo = MagicMock()
    mock_ingredient_repo = MagicMock()
    
    order_models = [
        create_mock_order_model(internal_id=1),
        create_mock_order_model(internal_id=2),
        create_mock_order_model(internal_id=3)
    ]
    
    mock_query = MagicMock()
    mock_session.query.return_value = mock_query
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = order_models
    
    mock_product_repo.find_by_id.return_value = create_mock_product()
    
    repo = SQLOrderRepository(mock_db, mock_product_repo, mock_ingredient_repo)
    
    # Act
    result = repo.list_all(skip=0, limit=10)
    
    # Assert
    assert len(result) == 3
    mock_query.offset.assert_called_once_with(0)
    mock_query.limit.assert_called_once_with(10)


def test_find_by_status_filters_correctly():
    """Given orders with specific status, when find_by_status is called, then filtered orders returned"""
    # Arrange
    mock_db = MagicMock()
    mock_session = MagicMock()
    mock_db.get_session.return_value.__enter__.return_value = mock_session
    
    mock_product_repo = MagicMock()
    mock_ingredient_repo = MagicMock()
    
    order_models = [
        create_mock_order_model(internal_id=1, status="RECEBIDO"),
        create_mock_order_model(internal_id=2, status="RECEBIDO")
    ]
    
    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_filter
    mock_filter.all.return_value = order_models
    
    mock_product_repo.find_by_id.return_value = create_mock_product()
    
    repo = SQLOrderRepository(mock_db, mock_product_repo, mock_ingredient_repo)
    
    # Act
    result = repo.get_by_status("RECEBIDO")
    
    # Assert
    assert len(result) == 2
    assert all(order.status.value == "RECEBIDO" for order in result)


def test_update_order_success():
    """Given existing order, when update is called, then order is updated in database"""
    # Arrange
    mock_db = MagicMock()
    mock_session = MagicMock()
    mock_db.get_session.return_value.__enter__.return_value = mock_session
    
    mock_product_repo = MagicMock()
    mock_ingredient_repo = MagicMock()
    
    order_model = create_mock_order_model(internal_id=1)
    
    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_filter
    mock_filter.first.return_value = order_model
    
    mock_product_repo.find_by_id.return_value = create_mock_product()
    
    # Create order entity with valid order items
    product = create_mock_product()
    order_item = OrderItem(
        order_internal_id=1,
        product=product,
        additional_ingredient=[],
        remove_ingredient=[]
    )
    
    order = Order(
        customer_internal_id=1,
        order_items=[order_item],
        value=Money(amount=60.0),
        status=OrderStatus.create("EM_PREPARACAO"),
        internal_id=1,
        _skip_active_validation=True
    )
    
    repo = SQLOrderRepository(mock_db, mock_product_repo, mock_ingredient_repo)
    
    # Act
    result = repo.update(order)
    
    # Assert
    assert result is not None
    assert order_model.value == 60.0
    assert order_model.status == "EM_PREPARACAO"
    mock_session.commit.assert_called()


def test_update_order_not_found():
    """Given non-existent order, when update is called, then ValueError is raised"""
    # Arrange
    mock_db = MagicMock()
    mock_session = MagicMock()
    mock_db.get_session.return_value.__enter__.return_value = mock_session
    
    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_filter
    mock_filter.first.return_value = None
    
    # Create valid order with items using correct OrderItem signature
    product = create_mock_product()
    order_item = OrderItem(
        order_internal_id=999,
        product=product,
        additional_ingredient=[],
        remove_ingredient=[]
    )
    
    order = Order(
        customer_internal_id=1,
        order_items=[order_item],
        value=Money(amount=50.0),
        status=OrderStatus.create("RECEBIDO"),
        internal_id=999,
        _skip_active_validation=True
    )
    
    repo = SQLOrderRepository(mock_db)
    
    # Act & Assert
    try:
        repo.update(order)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "not found" in str(e)


def test_cancel_order_success():
    """Given existing order, when cancel is called, then status is changed to CANCELADO"""
    # Arrange
    mock_db = MagicMock()
    mock_session = MagicMock()
    mock_db.get_session.return_value.__enter__.return_value = mock_session
    
    order_model = create_mock_order_model(internal_id=1, status="RECEBIDO")
    
    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_filter
    mock_filter.first.return_value = order_model
    
    repo = SQLOrderRepository(mock_db)
    
    # Act
    result = repo.cancel(1)
    
    # Assert
    assert result is True
    assert order_model.status == OrderStatusType.CANCELADO.value
    mock_session.commit.assert_called_once()


def test_cancel_order_not_found():
    """Given non-existent order, when cancel is called, then False is returned"""
    # Arrange
    mock_db = MagicMock()
    mock_session = MagicMock()
    mock_db.get_session.return_value.__enter__.return_value = mock_session
    
    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_filter
    mock_filter.first.return_value = None
    
    repo = SQLOrderRepository(mock_db)
    
    # Act
    result = repo.cancel(999)
    
    # Assert
    assert result is False


def test_update_status_success():
    """Given existing order, when update_status is called, then status is updated"""
    # Arrange
    mock_db = MagicMock()
    mock_session = MagicMock()
    mock_db.get_session.return_value.__enter__.return_value = mock_session
    
    mock_product_repo = MagicMock()
    mock_ingredient_repo = MagicMock()
    
    order_model = create_mock_order_model(internal_id=1, status="RECEBIDO")
    
    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_filter
    mock_filter.first.return_value = order_model
    
    mock_product_repo.find_by_id.return_value = create_mock_product()
    
    repo = SQLOrderRepository(mock_db, mock_product_repo, mock_ingredient_repo)
    
    # Act
    result = repo.update_status(1, "EM_PREPARACAO")
    
    # Assert
    assert result is not None
    assert order_model.status == "EM_PREPARACAO"
    mock_session.commit.assert_called()
    mock_session.refresh.assert_called()


def test_update_status_order_not_found():
    """Given non-existent order, when update_status is called, then None is returned"""
    # Arrange
    mock_db = MagicMock()
    mock_session = MagicMock()
    mock_db.get_session.return_value.__enter__.return_value = mock_session
    
    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_filter
    mock_filter.first.return_value = None
    
    repo = SQLOrderRepository(mock_db)
    
    # Act
    result = repo.update_status(999, "EM_PREPARACAO")
    
    # Assert
    assert result is None


def test_process_payment_approved():
    """Given approved payment, when process_payment is called, then payment is verified and status updated"""
    # Arrange
    mock_db = MagicMock()
    mock_session = MagicMock()
    mock_db.get_session.return_value.__enter__.return_value = mock_session
    
    mock_product_repo = MagicMock()
    mock_ingredient_repo = MagicMock()
    
    order_model = create_mock_order_model(internal_id=1, status="RECEBIDO")
    
    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_filter
    mock_filter.first.return_value = order_model
    
    mock_product_repo.find_by_id.return_value = create_mock_product()
    
    payment_data = {
        "transaction_id": "TXN123",
        "date": datetime.now(),
        "message": "Payment approved",
        "approval_status": True
    }
    
    repo = SQLOrderRepository(mock_db, mock_product_repo, mock_ingredient_repo)
    
    # Act
    result = repo.process_payment(1, payment_data)
    
    # Assert
    assert result is not None
    assert order_model.has_payment_verified is True
    assert order_model.payment_transaction_id == "TXN123"
    assert order_model.status == OrderStatusType.EM_PREPARACAO.value
    mock_session.commit.assert_called()


def test_process_payment_rejected():
    """Given rejected payment, when process_payment is called, then payment not verified and order cancelled"""
    # Arrange
    mock_db = MagicMock()
    mock_session = MagicMock()
    mock_db.get_session.return_value.__enter__.return_value = mock_session
    
    mock_product_repo = MagicMock()
    mock_ingredient_repo = MagicMock()
    
    order_model = create_mock_order_model(internal_id=1, status="RECEBIDO")
    
    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_filter
    mock_filter.first.return_value = order_model
    
    mock_product_repo.find_by_id.return_value = create_mock_product()
    
    payment_data = {
        "transaction_id": "TXN456",
        "date": datetime.now(),
        "message": "Payment rejected",
        "approval_status": False
    }
    
    repo = SQLOrderRepository(mock_db, mock_product_repo, mock_ingredient_repo)
    
    # Act
    result = repo.process_payment(1, payment_data)
    
    # Assert
    assert result is not None
    assert order_model.has_payment_verified is False
    assert order_model.status == OrderStatusType.CANCELADO.value
    mock_session.commit.assert_called()


def test_process_payment_order_not_found():
    """Given non-existent order, when process_payment is called, then None is returned"""
    # Arrange
    mock_db = MagicMock()
    mock_session = MagicMock()
    mock_db.get_session.return_value.__enter__.return_value = mock_session
    
    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_filter
    mock_filter.first.return_value = None
    
    payment_data = {"transaction_id": "TXN789", "approval_status": True}
    
    repo = SQLOrderRepository(mock_db)
    
    # Act
    result = repo.process_payment(999, payment_data)
    
    # Assert
    assert result is None


def test_get_payment_status_success():
    """Given order with payment, when get_payment_status is called, then payment dict is returned"""
    # Arrange
    mock_db = MagicMock()
    mock_session = MagicMock()
    mock_db.get_session.return_value.__enter__.return_value = mock_session
    
    order_model = create_mock_order_model(internal_id=1)
    order_model.payment_transaction_id = "TXN123"
    order_model.has_payment_verified = True
    order_model.payment_date = datetime(2026, 1, 6, 10, 0, 0)
    order_model.payment_message = "Approved"
    
    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_filter
    mock_filter.first.return_value = order_model
    
    repo = SQLOrderRepository(mock_db)
    
    # Act
    result = repo.get_payment_status(1)
    
    # Assert
    assert result is not None
    assert result["payment_transaction_id"] == "TXN123"
    assert result["has_payment_verified"] is True
    assert result["payment_message"] == "Approved"


def test_get_payment_status_order_not_found():
    """Given non-existent order, when get_payment_status is called, then None is returned"""
    # Arrange
    mock_db = MagicMock()
    mock_session = MagicMock()
    mock_db.get_session.return_value.__enter__.return_value = mock_session
    
    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_filter
    mock_filter.first.return_value = None
    
    repo = SQLOrderRepository(mock_db)
    
    # Act
    result = repo.get_payment_status(999)
    
    # Assert
    assert result is None


def test_to_entity_without_product_repository_raises_error():
    """Given order model with items but no product_repository, when _to_entity is called, then ValueError is raised"""
    # Arrange
    mock_db = MagicMock()
    
    order_model = create_mock_order_model(internal_id=1)
    
    # Add order item
    item_model = MagicMock(spec=OrderItemModel)
    item_model.internal_id = 1
    item_model.product_internal_id = 1
    item_model.additional_ingredient_internal_ids = []
    item_model.remove_ingredient_internal_ids = []
    item_model.item_receipt = []
    item_model.price = 10.0
    order_model.order_items = [item_model]
    
    repo = SQLOrderRepository(mock_db, product_repository=None)
    
    # Act & Assert
    try:
        repo._to_entity(order_model)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Product repository is required" in str(e)


def test_serialize_and_deserialize_ingredient_internal_ids():
    """Given list of ingredients, when serializing/deserializing internal_ids, then correct list is returned"""
    # Arrange
    mock_db = MagicMock()
    mock_session = MagicMock()
    
    ingredients = [
        create_mock_ingredient(internal_id=1),
        create_mock_ingredient(internal_id=2)
    ]
    
    repo = SQLOrderRepository(mock_db)
    
    # Act - Serialize
    serialized = repo._serialize_ingredient_internal_ids(ingredients, mock_session)
    
    # Assert - Serialize
    assert serialized == [1, 2]
    
    # Act - Deserialize
    deserialized = repo._deserialize_ingredient_internal_ids(serialized)
    
    # Assert - Deserialize
    assert deserialized == [1, 2]


def test_deserialize_ingredient_internal_ids_handles_none():
    """Given None or empty list, when deserializing internal_ids, then empty list is returned"""
    # Arrange
    mock_db = MagicMock()
    repo = SQLOrderRepository(mock_db)
    
    # Act & Assert
    assert repo._deserialize_ingredient_internal_ids(None) == []
    assert repo._deserialize_ingredient_internal_ids([]) == []
