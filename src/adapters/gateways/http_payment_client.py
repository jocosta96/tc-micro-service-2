import os
from typing import Optional, Dict, Any

import requests


class HTTPPaymentClient:
    """HTTP client for the payment-service."""

    def __init__(self, base_url: Optional[str] = None, timeout: int = 5):
        self.base_url = base_url or os.getenv("PAYMENT_API_HOST")
        self.timeout = timeout

    def request_payment(self, order_id: int, amount: float) -> Dict[str, Any]:
        if not self.base_url:
            raise ValueError("PAYMENT_API_HOST is not configured")

        url = f"http://{self.base_url}/payment/request/{order_id}"
        try:
            resp = requests.post(url, json={"amount": amount}, timeout=self.timeout)
        except Exception as exc:
            raise ValueError(f"Failed to reach payment service: {exc}") from exc

        if not resp.ok:
            raise ValueError(f"Payment service returned {resp.status_code}: {resp.text}")

        data = resp.json()
        if not data:
            raise ValueError("Payment service returned empty response")
        return data
