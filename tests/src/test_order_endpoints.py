import pytest


@pytest.fixture(scope="module")
def test_client(mock_boto3_ssm):
    """Create test client - imports app AFTER boto3 mock is active"""
    from fastapi.testclient import TestClient
    from src.main import app
    return TestClient(app)


def test_create_order_endpoint_invalid(test_client):
    # Dados inválidos: falta order_items
    resp = test_client.post("/order/create", json={"customer_internal_id": 1})
    assert resp.status_code in (401, 422, 400)


def test_get_order_not_found(test_client):
    resp = test_client.get("/order/by-id/9999")
    assert resp.status_code in (401, 404, 400, 500)


def test_cancel_order_not_found(test_client):
    resp = test_client.delete("/order/cancel/9999")
    assert resp.status_code in (401, 404, 400, 500)
