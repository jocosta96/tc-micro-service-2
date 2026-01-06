import pytest
from unittest.mock import MagicMock
from src.adapters.controllers.order_controller import OrderController
from src.application.repositories.order_repository import OrderRepository
from src.adapters.presenters.interfaces.presenter_interface import PresenterInterface
from src.application.dto.implementation.order_dto import OrderItemRequest, PaymentRequest
from datetime import datetime

class DummyPresenter(PresenterInterface):
    def present(self, data):
        return data
    def present_list(self, data_list):
        return {'data': data_list, 'total_count': len(data_list), 'timestamp': 'fake'}
    def present_error(self, exc):
        return str(exc)

class DummyOrderRepository(OrderRepository):
    def create(self, order):
        order.internal_id = 1
        return order
    def get_by_id(self, order_internal_id):
        return MagicMock(internal_id=order_internal_id)
    def get_by_status(self, status):
        return [MagicMock(status=status)]
    def list_all(self, skip=0, limit=100):
        return [MagicMock()]
    def update(self, order):
        return order
    def cancel(self, order_internal_id):
        return True
    def update_status(self, order_internal_id, status):
        return MagicMock(internal_id=order_internal_id, status=status)
    def process_payment(self, order_internal_id, payment_data):
        return MagicMock(internal_id=order_internal_id)
    def get_payment_status(self, order_internal_id):
        return {'status': 'PAID'}

def make_controller():
    repo = DummyOrderRepository()
    presenter = DummyPresenter()
    controller = OrderController(order_repository=repo, presenter=presenter)
    # Mock _fetch_catalog para evitar dependência de env
    for use_case in [controller.create_use_case]:
        if hasattr(use_case, '_fetch_catalog'):
            def fake_catalog(path):
                if '/customer/' in path:
                    return {
                        'is_active': True,
                        'is_anonymous': False,
                        'email': 'a@a.com',
                        'document': '123',
                        'internal_id': 1,
                        'name': 'Test',
                    }
                else:
                    from src.entities.product import ProductReceiptItem
                    from src.entities.ingredient import IngredientType
                    from src.entities.value_objects.name import Name
                    from src.entities.value_objects.money import Money
                    from src.entities.ingredient import Ingredient
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
                    from src.entities.value_objects.money import Money
                    return {
                        'is_active': True,
                        'internal_id': 1,
                        'name': 'Test',
                        'price': Money(amount=10.0),
                        'default_ingredient': [ProductReceiptItem(dummy_ing, 1)],
                        'category': 'burger',
                        'sku': 'ABC-1234-XYZ'
                    }
            use_case._fetch_catalog = fake_catalog
    return controller

def test_create_order_happy():
    controller = make_controller()
    data = {'customer_internal_id': 1, 'order_items': [{'product_internal_id': 1}]}
    resp = controller.create_order(data)
    # resp pode ser OrderResponse ou dict
    if hasattr(resp, 'internal_id'):
        assert resp.internal_id == 1
    else:
        assert resp['internal_id'] == 1

def test_create_order_invalid(monkeypatch):
    controller = make_controller()
    monkeypatch.setattr(controller.create_use_case, 'execute', lambda req: (_ for _ in ()).throw(ValueError('fail')))
    data = {'customer_internal_id': 1, 'order_items': [{'product_internal_id': 1}]}
    with pytest.raises(Exception):
        controller.create_order(data)

def test_get_order_found():
    controller = make_controller()
    resp = controller.get_order(1)
    assert resp is not None

def test_update_order_status():
    controller = make_controller()
    resp = controller.update_order_status(1, 'PRONTO')
    if hasattr(resp, 'status'):
        assert resp.status == 'PRONTO'
    else:
        assert resp['status'] == 'PRONTO'

def test_cancel_order():
    controller = make_controller()
    resp = controller.cancel_order(1)
    assert resp['message'] == 'Order canceled successfully'

def test_list_orders():
    controller = make_controller()
    resp = controller.list_orders()
    assert isinstance(resp, list) or isinstance(resp, dict) or hasattr(resp, 'orders')

def test_process_payment():
    controller = make_controller()
    data = {'transaction_id': 't', 'approval_status': True, 'date': datetime.now(), 'message': 'ok'}
    resp = controller.process_payment(1, data)
    if hasattr(resp, 'internal_id'):
        assert resp.internal_id == 1
    else:
        assert resp['internal_id'] == 1

def test_get_payment_status():
    controller = make_controller()
    resp = controller.get_payment_status(1)
    assert resp is not None

def test_request_payment(monkeypatch):
    controller = make_controller()
    controller.payment_request_use_case = MagicMock()
    controller.payment_request_use_case.execute.return_value = {'transaction_id': 't'}
    resp = controller.request_payment(1)
    assert resp['transaction_id'] == 't'

def test_get_orders_by_status():
    controller = make_controller()
    resp = controller.get_orders_by_status('RECEBIDO')
    assert isinstance(resp, list)
