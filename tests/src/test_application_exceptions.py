from src.application import exceptions


def test_custom_exceptions_str_repr():
    ex = exceptions.CustomerNotFoundException("not found")
    assert str(ex) == "not found"
    assert isinstance(repr(ex), str)
    ex2 = exceptions.OrderValidationException("bad order")
    assert str(ex2) == "bad order"
    assert isinstance(repr(ex2), str)
    ex3 = exceptions.PaymentException("pay error")
    assert str(ex3) == "pay error"
    assert isinstance(repr(ex3), str)
    # test base
    base = exceptions.ApplicationException("base")
    assert str(base) == "base"
    assert isinstance(repr(base), str)
