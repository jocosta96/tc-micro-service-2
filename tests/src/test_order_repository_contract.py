from src.application.repositories.order_repository import OrderRepository
from src.entities.order import Order, OrderItem
from src.entities.product import Product
from src.entities.ingredient import Ingredient
from src.entities.value_objects.money import Money
from unittest.mock import MagicMock

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

def test_order_repository_contract():
    class Repo(OrderRepository):
        def create(self, order): return order
        def get_by_id(self, order_internal_id): return MagicMock()
        def get_by_status(self, status): return [MagicMock()]
        def list_all(self, skip=0, limit=100): return [MagicMock()]
        def update(self, order): return order
        def cancel(self, order_internal_id): return True
        def update_status(self, order_internal_id, status): return MagicMock()
        def process_payment(self, order_internal_id, payment_data): return MagicMock()
        def get_payment_status(self, order_internal_id): return {'status': 'PAID'}
    repo = Repo()
    item = OrderItem(order_internal_id=1, product=DummyProduct(), additional_ingredient=[], remove_ingredient=[])
    order = Order.create(customer_internal_id=1, order_items=[item])
    assert repo.create(order) == order
    assert repo.get_by_id(1) is not None
    assert isinstance(repo.get_by_status('RECEBIDO'), list)
    assert isinstance(repo.list_all(), list)
    assert repo.update(order) == order
    assert repo.cancel(1) is True
    assert repo.update_status(1, 'PRONTO') is not None
    assert repo.process_payment(1, {}) is not None
    assert repo.get_payment_status(1)['status'] == 'PAID'
