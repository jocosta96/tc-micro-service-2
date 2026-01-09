from src.adapters.presenters.implementations.json_presenter import JSONPresenter
from src.application.dto.implementation.order_dto import OrderResponse
from src.entities.order import Order, OrderItem
from src.entities.product import Product, ProductCategory, ProductReceiptItem
from src.entities.ingredient import Ingredient, IngredientType
from src.entities.value_objects.money import Money
from src.entities.value_objects.name import Name
from src.entities.value_objects.sku import SKU


class DummyError(Exception):
    pass


def make_order_response():
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
    prod = Product(
        name=Name.create("Burger"),
        price=Money(amount=10.0),
        category=ProductCategory.BURGER,
        sku=SKU.create("ABC-1234-XYZ"),
        default_ingredient=[ProductReceiptItem(ing, 1)],
        is_active=True,
        internal_id=1,
    )
    item = OrderItem(
        order_internal_id=1,
        product=prod,
        additional_ingredient=[],
        remove_ingredient=[],
    )
    order = Order.create(customer_internal_id=1, order_items=[item])
    return OrderResponse.from_entity(order)


def test_presenter_present():
    presenter = JSONPresenter()
    data = make_order_response()
    result = presenter.present(data)
    assert isinstance(result, dict)
    assert "internal_id" in result


def test_presenter_present_list():
    presenter = JSONPresenter()
    data = [make_order_response(), make_order_response()]
    result = presenter.present_list(data)
    assert isinstance(result, dict)
    assert "data" in result
    assert result["total_count"] == 2


def test_presenter_present_error():
    presenter = JSONPresenter()
    err = DummyError("fail")
    result = presenter.present_error(err)
    assert "error" in result
    assert result["error"]["type"] == "DummyError"
    assert result["error"]["message"] == "fail"
