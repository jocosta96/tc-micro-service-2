import pytest
from src.entities.order import Order, OrderItem
from src.entities.product import Product, ProductCategory, ProductReceiptItem
from src.entities.ingredient import Ingredient, IngredientType
from src.entities.value_objects.money import Money
from src.entities.value_objects.name import Name
from src.entities.value_objects.sku import SKU
from src.entities.value_objects.order_status import OrderStatus
from datetime import datetime

def make_dummy_product():
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
    return Product(
        name=Name.create('Burger'),
        price=Money(amount=10.0),
        category=ProductCategory.BURGER,
        sku=SKU.create('ABC-1234-XYZ'),
        default_ingredient=[ProductReceiptItem(dummy_ing, 1)],
        is_active=True,
        internal_id=1
    )

def test_order_create_with_items_factory():
    prod1 = make_dummy_product()
    prod2 = make_dummy_product()
    order = Order.create_with_items(
        customer_internal_id=1,
        products=[prod1, prod2],
        additional_ingredients=[[ ], [ ]],
        remove_ingredients=[[ ], [ ]]
    )
    assert len(order.order_items) == 2
    assert order.customer_internal_id == 1

def test_order_validate_business_rules_skip_active():
    prod = make_dummy_product()
    item = OrderItem(order_internal_id=1, product=prod, additional_ingredient=[], remove_ingredient=[])
    order = Order(
        customer_internal_id=1,
        order_items=[item],
        value=Money(amount=10.0),
        status=OrderStatus.create('RECEBIDO'),
        _skip_active_validation=True
    )
    assert order.customer_internal_id == 1
    assert order.value.amount == 10.0
