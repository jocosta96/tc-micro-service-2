from src.entities.product import Product, ProductCategory, ProductReceiptItem
from src.entities.ingredient import Ingredient, IngredientType
from src.entities.value_objects.money import Money
from src.entities.value_objects.name import Name
from src.entities.value_objects.sku import SKU


def make_dummy_ingredient():
    return Ingredient(
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


def test_product_str_repr():
    ing = make_dummy_ingredient()
    prod = Product(
        name=Name.create("Burger"),
        price=Money(amount=10.0),
        category=ProductCategory.BURGER,
        sku=SKU.create("ABC-1234-XYZ"),
        default_ingredient=[ProductReceiptItem(ing, 1)],
        is_active=True,
        internal_id=1,
    )
    s = str(prod)
    r = repr(prod)
    assert "Product" in s
    assert "Product" in r


def test_product_update():
    ing = make_dummy_ingredient()
    prod = Product(
        name=Name.create("Burger"),
        price=Money(amount=10.0),
        category=ProductCategory.BURGER,
        sku=SKU.create("ABC-1234-XYZ"),
        default_ingredient=[ProductReceiptItem(ing, 1)],
        is_active=True,
        internal_id=1,
    )
    prod.update(
        "X-Burger", 15.0, "burger", "DEF-5678-XYZ", [ProductReceiptItem(ing, 2)]
    )
    assert prod.name.value == "X-Burger"
    assert prod.price.value == 15.0
    assert prod.sku.value == "DEF-5678-XYZ"
    assert prod.default_ingredient[0].quantity == 2


def test_product_create_registered():
    ing = make_dummy_ingredient()
    prod = Product.create_registered(
        name="Burger",
        price=10.0,
        category="burger",
        sku="ABC-1234-XYZ",
        default_ingredient=[ProductReceiptItem(ing, 1)],
    )
    assert isinstance(prod, Product)
    assert prod.category == ProductCategory.BURGER
    assert prod.sku.value == "ABC-1234-XYZ"
