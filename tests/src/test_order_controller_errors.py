import pytest
from unittest.mock import MagicMock
from src.adapters.controllers.order_controller import OrderController
from src.application.dto.implementation.order_dto import OrderUpdateRequest
from fastapi import HTTPException

class DummyPresenter:
    def present(self, data):
        return data
    def present_error(self, exc):
        return str(exc)

class DummyUseCase:
    def execute(self, *args, **kwargs):
        return None

@pytest.fixture
def controller():
    ctrl = OrderController(order_repository=MagicMock(), presenter=DummyPresenter())
    ctrl.read_use_case = DummyUseCase()
    ctrl.update_use_case = DummyUseCase()
    ctrl.cancel_use_case = DummyUseCase()
    return ctrl

def test_get_order_not_found(controller):
    with pytest.raises(HTTPException) as exc:
        controller.get_order(1)
    assert exc.value.status_code == 404

def test_update_order_not_found(controller):
    with pytest.raises(HTTPException) as exc:
        controller.update_order(1, {})
    assert exc.value.status_code == 404

def test_cancel_order_not_found(controller):
    with pytest.raises(HTTPException) as exc:
        controller.cancel_order(1)
    assert exc.value.status_code == 404

def test_update_order_value_error(controller, monkeypatch):
    class FailingUseCase:
        def execute(self, *a, **k):
            raise ValueError('bad')
    controller.update_use_case = FailingUseCase()
    with pytest.raises(HTTPException) as exc:
        controller.update_order(1, {})
    assert exc.value.status_code == 400

def test_update_order_generic_error(controller, monkeypatch):
    class FailingUseCase:
        def execute(self, *a, **k):
            raise RuntimeError('fail')
    controller.update_use_case = FailingUseCase()
    with pytest.raises(HTTPException) as exc:
        controller.update_order(1, {})
    assert exc.value.status_code == 500
