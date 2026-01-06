import pytest
from src.entities.ingredient import Ingredient, IngredientType
from src.entities.value_objects.money import Money
from src.entities.value_objects.name import Name


def test_ingredient_str_repr():
    ing = Ingredient(
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
    s = str(ing)
    r = repr(ing)
    assert "Ingredient" in s
    assert "Ingredient" in r


def test_ingredient_invalid_type():
    with pytest.raises(ValueError):
        Ingredient(
            name=Name.create("Queijo"),
            price=Money(amount=1.0),
            is_active=True,
            type=None,
            applies_to_burger=True,
            applies_to_side=False,
            applies_to_drink=False,
            applies_to_dessert=False,
            internal_id=1,
        )


def test_ingredient_invalid_usage():
    with pytest.raises(ValueError):
        Ingredient(
            name=Name.create("Queijo"),
            price=Money(amount=1.0),
            is_active=True,
            type=IngredientType.CHEESE,
            applies_to_burger=False,
            applies_to_side=False,
            applies_to_drink=False,
            applies_to_dessert=False,
            internal_id=1,
        )
