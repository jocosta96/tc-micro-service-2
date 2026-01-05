import pytest
from src.entities.value_objects.money import Money
from src.entities.value_objects.name import Name
from src.entities.value_objects.sku import SKU
from src.entities.value_objects.order_status import OrderStatus, OrderStatusType

def test_money_str_repr_add():
    m1 = Money(amount=10.0)
    m2 = Money(amount=5.0)
    s = str(m1)
    r = repr(m1)
    assert 'Money' in r
    m3 = m1 + m2
    assert isinstance(m3, Money)
    assert m3.amount == 15.0

def test_money_invalid():
    with pytest.raises(ValueError):
        Money(amount=-1.0)
    with pytest.raises(ValueError):
        Money(amount=1.123)

def test_name_create_and_str():
    n = Name.create('joao')
    assert isinstance(n, Name)
    assert str(n) == 'Joao'

def test_sku_create_and_str():
    sku = SKU.create('abc-1234-xyz')
    assert isinstance(sku, SKU)
    assert str(sku) == 'ABC-1234-XYZ'
    with pytest.raises(ValueError):
        SKU.create('invalid')

def test_order_status_create_and_next():
    s = OrderStatus.create('RECEBIDO')
    assert s.status == OrderStatusType.RECEBIDO
    next_s = s.next_status()
    assert next_s.status == OrderStatusType.EM_PREPARACAO
    assert str(s) == 'RECEBIDO'
    assert s.value == 'RECEBIDO'
    with pytest.raises(ValueError):
        OrderStatus.create('INVALID')
