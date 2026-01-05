import pytest
from src.entities.order import Order, OrderItem
from src.entities.product import Product
from src.entities.ingredient import Ingredient
from src.entities.value_objects.money import Money
from src.entities.value_objects.order_status import OrderStatus
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

def test_order_create_happy_path():
    item = make_order_item()
    order = Order.create(customer_internal_id=1, order_items=[item])
    assert order.customer_internal_id == 1
    assert len(order.order_items) == 1
    assert order.status is not None
    assert order.value.amount > 0

def test_order_create_no_items_raises():
    with pytest.raises(ValueError):
        Order.create(customer_internal_id=1, order_items=[])

def test_order_create_inactive_product_raises():
    inactive_product = DummyProduct(is_active=False)
    item = make_order_item(product=inactive_product)
    with pytest.raises(ValueError):
        Order.create(customer_internal_id=1, order_items=[item])

def test_order_process_payment_approved():
    item = make_order_item()
    order = Order.create(customer_internal_id=1, order_items=[item])
    payment = {'transaction_id': 'abc', 'approval_status': True, 'date': datetime.now(), 'message': 'ok'}
    order.process_payment(payment)
    assert order.has_payment_verified is True
    assert str(order.status) == 'EM_PREPARACAO'

def test_order_process_payment_rejected():
    item = make_order_item()
    order = Order.create(customer_internal_id=1, order_items=[item])
    payment = {'transaction_id': 'abc', 'approval_status': False, 'date': datetime.now(), 'message': 'fail'}
    order.process_payment(payment)
    assert order.has_payment_verified is False
    assert str(order.status) == 'CANCELADO'

def test_order_process_payment_duplicate_raises():
    item = make_order_item()
    order = Order.create(customer_internal_id=1, order_items=[item])
    payment = {'transaction_id': 'abc', 'approval_status': True, 'date': datetime.now(), 'message': 'ok'}
    order.process_payment(payment)
    with pytest.raises(ValueError):
        order.process_payment(payment)
