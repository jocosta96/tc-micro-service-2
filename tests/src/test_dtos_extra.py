from src.application.dto.implementation.order_dto import OrderItemRequest
from src.application.dto.implementation.order_dto import OrderCreateRequest
from src.application.dto.implementation.order_dto import OrderUpdateRequest
from src.application.dto.implementation.order_dto import PaymentRequest
from datetime import datetime


def test_order_item_request_defaults():
    req = OrderItemRequest(product_internal_id=1)
    assert req.additional_ingredient_internal_ids == []
    assert req.remove_ingredient_internal_ids == []


def test_order_create_request_to_dict_empty():
    req = OrderCreateRequest(customer_internal_id=1, order_items=[])
    d = req.to_dict()
    assert d["order_items"] == []


def test_order_update_request_to_dict_none():
    req = OrderUpdateRequest()
    d = req.to_dict()
    assert d["status"] is None
    assert d["order_items"] is None


def test_payment_request_to_dict_empty_message():
    req = PaymentRequest(transaction_id="t", approval_status=True, date=datetime.now())
    d = req.to_dict()
    assert d["message"] == ""
