from src.entities.order import Order, OrderItem
from src.entities.product import Product, ProductCategory, ProductReceiptItem
from src.entities.ingredient import Ingredient, IngredientType
from src.entities.value_objects.money import Money
from src.entities.value_objects.name import Name
from src.entities.value_objects.sku import SKU


def make_dummy_product():
    dummy_ing = Ingredient(
        name=Name.create("Queijo"),
        price=Money(amount=1.0),
        is_active=True,
        type=IngredientType.CHEESE,
        applies_to_burger=True,
        applies_to_side=False,
        applies_to_drink=False,
        applies_to_dessert=False,
        internal_id=1,
    )
    return Product(
        name=Name.create("Burger"),
        price=Money(amount=10.0),
        category=ProductCategory.BURGER,
        sku=SKU.create("ABC-1234-XYZ"),
        default_ingredient=[ProductReceiptItem(dummy_ing, 1)],
        is_active=True,
        internal_id=1,
    )


def test_order_str_repr():
    item = OrderItem(
        order_internal_id=1,
        product=make_dummy_product(),
        additional_ingredient=[],
        remove_ingredient=[],
    )
    order = Order.create(customer_internal_id=1, order_items=[item])
    s = str(order)
    r = repr(order)
    assert "Order" in s
    assert "Order" in r


def test_order_update_display_id():
    item = OrderItem(
        order_internal_id=1,
        product=make_dummy_product(),
        additional_ingredient=[],
        remove_ingredient=[],
    )
    order = Order.create(customer_internal_id=1, order_items=[item], internal_id=42)
    order.order_display_id = ""
    display_id = order.update_display_id()
    assert display_id == "042"
    assert order.order_display_id == "042"


def test_order_next_status_and_previous_status():
    item = OrderItem(
        order_internal_id=1,
        product=make_dummy_product(),
        additional_ingredient=[],
        remove_ingredient=[],
    )
    order = Order.create(customer_internal_id=1, order_items=[item])
    s1 = order.status
    order.next_status()
    s2 = order.status
    assert s2 != s1
    # Test previous_status via value object
    prev = s2.previous_status()
    assert prev.status == s1.status
