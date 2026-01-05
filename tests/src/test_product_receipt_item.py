import pytest
from src.entities.product import ProductReceiptItem
from src.entities.ingredient import Ingredient, IngredientType
from src.entities.value_objects.money import Money
from src.entities.value_objects.name import Name

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

def test_product_receipt_item_tuple():
    ing = make_dummy_ingredient()
    item = ProductReceiptItem(ingredient=ing, quantity=2)
    t = item.__tuple__()
    assert t[0] == ing
    assert t[1] == 2
