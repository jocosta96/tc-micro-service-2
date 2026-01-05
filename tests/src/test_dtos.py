import pytest
from src.application.dto.implementation.order_dto import (
    OrderItemRequest, OrderCreateRequest, OrderUpdateRequest, PaymentRequest,
    PaymentRequestResponse, OrderItemResponse, OrderResponse, OrderListResponse, PaymentStatusResponse
)
from datetime import datetime

def test_order_item_request_to_dict():
    req = OrderItemRequest(product_internal_id=1, additional_ingredient_internal_ids=[2], remove_ingredient_internal_ids=[3])
    d = req.to_dict()
    assert d['product_internal_id'] == 1
    assert d['additional_ingredient_internal_ids'] == [2]
    assert d['remove_ingredient_internal_ids'] == [3]

def test_order_create_request_to_dict():
    item = OrderItemRequest(product_internal_id=1, additional_ingredient_internal_ids=[], remove_ingredient_internal_ids=[])
    req = OrderCreateRequest(customer_internal_id=1, order_items=[item])
    d = req.to_dict()
    assert d['customer_internal_id'] == 1
    assert isinstance(d['order_items'], list)

def test_order_update_request_to_dict():
    req = OrderUpdateRequest(status='PRONTO', order_items=None)
    d = req.to_dict()
    assert d['status'] == 'PRONTO'
    assert d['order_items'] is None

def test_payment_request_to_dict():
    req = PaymentRequest(transaction_id='t', approval_status=True, date=datetime.now(), message='ok')
    d = req.to_dict()
    assert d['transaction_id'] == 't'
    assert d['approval_status'] is True
    assert 'date' in d
    assert d['message'] == 'ok'

def test_payment_request_response_to_dict():
    resp = PaymentRequestResponse(order_id=1, amount=10.0, transaction_id='t', payment_url='url', expires_at='now')
    d = resp.to_dict()
    assert d['order_id'] == 1
    assert d['amount'] == 10.0
    assert d['transaction_id'] == 't'
    assert d['payment_url'] == 'url'
    assert d['expires_at'] == 'now'

def test_order_item_response_to_dict():
    resp = OrderItemResponse(
        internal_id=1, product_internal_id=1, product_name='Burger', product_price=10.0,
        additional_ingredients=[2], remove_ingredients=[3], item_receipt=[{'ingredient_internal_id': 2, 'ingredient_name': 'Queijo', 'quantity': 1}], price=10.0
    )
    d = resp.to_dict()
    assert d['internal_id'] == 1
    assert d['product_name'] == 'Burger'
    assert d['price'] == 10.0

def test_order_response_to_dict():
    resp = OrderResponse(
        internal_id=1, customer_internal_id=1, order_items=[], value=10.0, status='RECEBIDO',
        start_date=None, end_date=None, has_payment_verified=False, payment_date=None,
        payment_transaction_id='', payment_message='', order_display_id='001'
    )
    d = resp.to_dict()
    assert d['internal_id'] == 1
    assert d['customer_internal_id'] == 1
    assert d['value'] == 10.0
    assert d['status'] == 'RECEBIDO'

def test_order_list_response_to_dict():
    resp = OrderListResponse(orders=[], total=0, skip=0, limit=10)
    d = resp.to_dict()
    assert d['orders'] == []
    assert d['total'] == 0
    assert d['skip'] == 0
    assert d['limit'] == 10

def test_payment_status_response_to_dict():
    resp = PaymentStatusResponse(order_internal_id=1, payment_date=None, payment_transaction_id='t', payment_message='ok', has_payment_verified=True, value=10.0, status='RECEBIDO')
    d = resp.to_dict()
    assert d['order_internal_id'] == 1
    assert d['has_payment_verified'] is True
    assert d['value'] == 10.0
    assert d['status'] == 'RECEBIDO'
