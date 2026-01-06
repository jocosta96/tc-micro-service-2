from src.entities.order import OrderItem
from src.entities.product import Product, ProductCategory, ProductReceiptItem
from src.entities.ingredient import Ingredient, IngredientType
from src.entities.value_objects.money import Money
from src.entities.value_objects.name import Name
from src.entities.value_objects.sku import SKU

def make_dummy_ingredient():
    return Ingredient(
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

def make_dummy_product():
    ing = make_dummy_ingredient()
    return Product(
        name=Name.create('Burger'),
        price=Money(amount=10.0),
        category=ProductCategory.BURGER,
        sku=SKU.create('ABC-1234-XYZ'),
        default_ingredient=[ProductReceiptItem(ing, 1)],
        is_active=True,
        internal_id=1
    )

def test_order_item_str_repr():
    item = OrderItem(order_internal_id=1, product=make_dummy_product(), additional_ingredient=[], remove_ingredient=[])
    s = str(item)
    r = repr(item)
    assert 'OrderItem' in s
    assert 'OrderItem' in r

def test_order_item_get_item_receipt():
    item = OrderItem(order_internal_id=1, product=make_dummy_product(), additional_ingredient=[], remove_ingredient=[])
    receipt = item.get_item_receipt()
    assert isinstance(receipt, list)
    assert len(receipt) > 0

def test_order_item_calculate_price_with_additional():
    ing = make_dummy_ingredient()
    item = OrderItem(order_internal_id=1, product=make_dummy_product(), additional_ingredient=[ing], remove_ingredient=[])
    item._calculate_price()
    assert item.price.amount > 0
