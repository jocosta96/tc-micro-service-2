import pytest
from unittest.mock import MagicMock
from src.application.use_cases.order_use_cases import (
    OrderCreateUseCase, OrderReadUseCase, OrderUpdateUseCase, OrderCancelUseCase,
    OrderStatusUpdateUseCase, OrderPaymentProcessUseCase, OrderPaymentStatusUseCase, OrderPaymentRequestUseCase, OrderByStatusUseCase
)
from src.application.dto.implementation.order_dto import (
    OrderCreateRequest, OrderItemRequest, OrderUpdateRequest, PaymentRequest
)
from src.entities.order import Order, OrderItem
from src.entities.product import Product
from src.entities.ingredient import Ingredient
from src.entities.value_objects.money import Money
from datetime import datetime

from src.entities.value_objects.name import Name
from src.entities.value_objects.sku import SKU
from src.entities.product import ProductCategory, ProductReceiptItem
from src.entities.ingredient import IngredientType

class DummyIngredient(Ingredient):
    def __init__(self, internal_id=1, name='Ing', price=Money(amount=1.0), is_active=True):
        super().__init__(
            name=Name.create(name),
            price=price,
            is_active=is_active,
            type=IngredientType.CHEESE,
            applies_to_burger=True,
            applies_to_side=False,
            applies_to_drink=False,
            applies_to_dessert=False,
            internal_id=internal_id
        )

class DummyProduct(Product):
    def __init__(self, internal_id=1, name='Test', price=Money(amount=10.0), is_active=True, default_ingredient=None, category=ProductCategory.BURGER, sku=None):
        if default_ingredient is None:
            dummy_ing = DummyIngredient()
            default_ingredient = [ProductReceiptItem(dummy_ing, 1)]
        if sku is None:
            sku = SKU.create('ABC-1234-XYZ')
        super().__init__(
            name=Name.create(name),
            price=price,
            category=category,
            sku=sku,
            default_ingredient=default_ingredient,
            is_active=is_active,
            internal_id=internal_id
        )

def make_order_item(product=None, additional=None, remove=None):
    if product is None:
        product = DummyProduct()
    if additional is None:
        additional = []
    if remove is None:
        remove = []
    return OrderItem(order_internal_id=1, product=product, additional_ingredient=additional, remove_ingredient=remove)

def make_order():
    item = make_order_item()
    return Order.create(customer_internal_id=1, order_items=[item])

def test_order_read_use_case():
    repo = MagicMock()
    order = make_order()
    repo.get_by_id.return_value = order
    use_case = OrderReadUseCase(repo)
    resp = use_case.execute(order.internal_id)
    assert resp.internal_id == order.internal_id

def test_order_update_use_case_status():
    repo = MagicMock()
    order = make_order()
    repo.get_by_id.return_value = order
    repo.update.return_value = order
    use_case = OrderUpdateUseCase(repo)
    req = OrderUpdateRequest(status='PRONTO')
    resp = use_case.execute(order.internal_id, req)
    assert resp.status == 'PRONTO'

def test_order_cancel_use_case():
    repo = MagicMock()
    repo.cancel.return_value = True
    use_case = OrderCancelUseCase(repo)
    assert use_case.execute(1) is True

def test_order_status_update_use_case():
    repo = MagicMock()
    order = make_order()
    repo.update_status.return_value = order
    use_case = OrderStatusUpdateUseCase(repo)
    resp = use_case.execute(order.internal_id, 'PRONTO')
    assert resp.internal_id == order.internal_id

def test_order_payment_process_use_case():
    repo = MagicMock()
    order = make_order()
    repo.process_payment.return_value = order
    use_case = OrderPaymentProcessUseCase(repo)
    req = PaymentRequest(transaction_id='t', approval_status=True, date=datetime.now(), message='ok')
    resp = use_case.execute(order.internal_id, req)
    assert resp.internal_id == order.internal_id

def test_order_payment_status_use_case():
    repo = MagicMock()
    order = make_order()
    repo.get_by_id.return_value = order
    use_case = OrderPaymentStatusUseCase(repo)
    resp = use_case.execute(order.internal_id)
    assert resp.order_internal_id == order.internal_id

def test_order_payment_request_use_case_happy():
    repo = MagicMock()
    order = make_order()
    order.has_payment_verified = False
    repo.get_by_id.return_value = order
    payment_client = MagicMock()
    payment_client.request_payment.return_value = {'transaction_id': 't', 'payment_url': 'url', 'expires_at': 'now', 'qr_code': None, 'link': None}
    use_case = OrderPaymentRequestUseCase(repo, payment_client)
    resp = use_case.execute(order.internal_id)
    assert resp.transaction_id == 't'
    assert resp.payment_url == 'url'

def test_order_payment_request_use_case_already_paid():
    repo = MagicMock()
    order = make_order()
    order.has_payment_verified = True
    repo.get_by_id.return_value = order
    payment_client = MagicMock()
    use_case = OrderPaymentRequestUseCase(repo, payment_client)
    with pytest.raises(ValueError):
        use_case.execute(order.internal_id)

def test_order_by_status_use_case():
    repo = MagicMock()
    order = make_order()
    repo.get_by_status.return_value = [order]
    use_case = OrderByStatusUseCase(repo)
    resp = use_case.execute('RECEBIDO')
    assert len(resp) == 1
    assert resp[0].internal_id == order.internal_id

def test_order_create_use_case_happy(monkeypatch):
    repo = MagicMock()
    use_case = OrderCreateUseCase(repo)
    # Patch _fetch_catalog to return valid customer/product/ingredient
    def fake_catalog(path):
        if '/customer/' in path:
            return {
                'is_active': True,
                'is_anonymous': False,
                'email': 'a@a.com',
                'document': '123',
                'internal_id': 1,
                'name': 'Test',
            }
        else:
            from src.entities.product import ProductReceiptItem
            from src.entities.ingredient import IngredientType
            from src.entities.value_objects.name import Name
            from src.entities.value_objects.money import Money
            from src.entities.ingredient import Ingredient
            dummy_ing = Ingredient(
                name=Name.create('Queijo'),
                price=Money(amount=1.0),
                is_active=True,
                type=IngredientType.CHEESE,
                applies_to_burger=True,
                applies_to_side=False,
                applies_to_drink=False,
                applies_to_dessert=False,
                internal_id=1
            )
            from src.entities.value_objects.money import Money
            return {
                'is_active': True,
                'internal_id': 1,
                'name': 'Test',
                'price': Money(amount=10.0),
                'default_ingredient': [ProductReceiptItem(dummy_ing, 1)],
                'category': 'burger',
                'sku': 'ABC-1234-XYZ'
            }
    monkeypatch.setattr(use_case, '_fetch_catalog', fake_catalog)
    item_req = OrderItemRequest(product_internal_id=1, additional_ingredient_internal_ids=[], remove_ingredient_internal_ids=[])
    req = OrderCreateRequest(customer_internal_id=1, order_items=[item_req])
    # Mock repo.create para retornar um Order real
    def repo_create(order):
        return Order.create(customer_internal_id=order.customer_internal_id, order_items=order.order_items)
    repo.create.side_effect = repo_create
    resp = use_case.execute(req)
    assert resp.customer_internal_id == 1

def test_order_create_use_case_inactive_customer(monkeypatch):
    repo = MagicMock()
    use_case = OrderCreateUseCase(repo)
    monkeypatch.setattr(use_case, '_fetch_catalog', lambda path: {
        'is_active': False,
        'email': 'a@a.com',
        'document': '123',
        'internal_id': 1,
        'name': 'Test',
        'price': 10.0,
        'default_ingredient': [],
        'category': 'burger',
        'sku': 'ABC-1234-XYZ',
        'type': 'cheese',
        'applies_to_burger': True,
        'applies_to_side': False,
        'applies_to_drink': False,
        'applies_to_dessert': False,
        'quantity': 1
    })
    item_req = OrderItemRequest(product_internal_id=1, additional_ingredient_internal_ids=[], remove_ingredient_internal_ids=[])
    req = OrderCreateRequest(customer_internal_id=1, order_items=[item_req])
    with pytest.raises(ValueError):
        use_case.execute(req)

def test_order_create_use_case_missing_catalog(monkeypatch):
    repo = MagicMock()
    use_case = OrderCreateUseCase(repo)
    monkeypatch.setattr(use_case, '_fetch_catalog', lambda path: None)
    item_req = OrderItemRequest(product_internal_id=1, additional_ingredient_internal_ids=[], remove_ingredient_internal_ids=[])
    req = OrderCreateRequest(customer_internal_id=1, order_items=[item_req])
    with pytest.raises(ValueError):
        use_case.execute(req)
