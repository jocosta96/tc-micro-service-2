import os
from typing import Optional, Dict, Any

import requests


class HTTPPaymentClient:
    """HTTP client for the payment-service."""

    def __init__(self, base_url: Optional[str] = None, timeout: int = 5):
        self.base_url = base_url or os.getenv("PAYMENT_API_HOST")
        self.timeout = timeout
        self.webhook_url = os.getenv("WEBHOOK_URL", "http://localhost:8000")

    def request_payment(self, order_id: int, amount: float) -> Dict[str, Any]:
        if not self.base_url:
            raise ValueError("PAYMENT_API_HOST is not configured")

        # Use HTTP for local development. Set PAYMENT_API_HOST without protocol.
        url = f"http://{self.base_url}/payment/request/{order_id}"
        
        # Include webhook URL for payment confirmation callback
        payload = {
            "amount": amount,
            "webhook_url": f"{self.webhook_url}/order/payment_confirm/{order_id}"
        }
        
        try:
            resp = requests.post(url, json=payload, timeout=self.timeout)
        except Exception as exc:
            raise ValueError(f"Failed to reach payment service: {exc}") from exc

        if not resp.ok:
            raise ValueError(
                f"Payment service returned {resp.status_code}: {resp.text}"
            )

        data = resp.json()
        if not data:
            raise ValueError("Payment service returned empty response")
        return data
