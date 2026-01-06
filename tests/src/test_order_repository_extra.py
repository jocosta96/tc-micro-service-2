from src.application.repositories.order_repository import OrderRepository
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


def make_order():
    item = OrderItem(
        order_internal_id=1,
        product=make_dummy_product(),
        additional_ingredient=[],
        remove_ingredient=[],
    )
    return Order.create(customer_internal_id=1, order_items=[item])


def test_order_repository_list_all():
    class Repo(OrderRepository):
        def create(self, order):
            return order

        def get_by_id(self, order_internal_id):
            return make_order()

        def get_by_status(self, status):
            return [make_order()]

        def list_all(self, skip=0, limit=100):
            return [make_order()]

        def update(self, order):
            return order

        def cancel(self, order_internal_id):
            return True

        def update_status(self, order_internal_id, status):
            return make_order()

        def process_payment(self, order_internal_id, payment_data):
            return make_order()

        def get_payment_status(self, order_internal_id):
            return {"status": "PAID"}

    repo = Repo()
    assert isinstance(repo.list_all(), list)
    assert repo.cancel(1) is True
    assert repo.update_status(1, "PRONTO") is not None
    assert repo.process_payment(1, {}) is not None
    assert repo.get_payment_status(1)["status"] == "PAID"
