from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_create_order_endpoint_invalid():
    # Dados inválidos: falta order_items
    resp = client.post("/order/create", json={"customer_internal_id": 1})
    assert resp.status_code in (401, 422, 400)


def test_get_order_not_found():
    resp = client.get("/order/by-id/9999")
    assert resp.status_code in (401, 404, 400, 500)


def test_cancel_order_not_found():
    resp = client.delete("/order/cancel/9999")
    assert resp.status_code in (401, 404, 400, 500)
