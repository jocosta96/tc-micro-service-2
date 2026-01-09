import pytest
from unittest.mock import patch, MagicMock
from src.adapters.gateways.http_payment_client import HTTPPaymentClient


class TestHTTPPaymentClient:
    @patch("src.adapters.gateways.http_payment_client.get_ssm_client")
    @patch("src.adapters.gateways.http_payment_client.requests.post")
    def test_request_payment_success(self, mock_post, mock_ssm):
        # Mock SSM client
        mock_ssm_client = MagicMock()
        mock_ssm_client.get_parameter.return_value = None
        mock_ssm.return_value = mock_ssm_client
        # Given dados válidos
        mock_post.return_value.status_code = 200
        mock_post.return_value.ok = True
        mock_post.return_value.json.return_value = {"status": "ok"}
        client = HTTPPaymentClient("fake-url")
        # When
        resp = client.request_payment(order_id=1, amount=10)
        # Then retorna sucesso
        assert resp["status"] == "ok"

    @patch("src.adapters.gateways.http_payment_client.get_ssm_client")
    @patch("src.adapters.gateways.http_payment_client.requests.post")
    def test_request_payment_timeout(self, mock_post, mock_ssm):
        # Mock SSM client
        mock_ssm_client = MagicMock()
        mock_ssm_client.get_parameter.return_value = None
        mock_ssm.return_value = mock_ssm_client
        # Given timeout
        mock_post.side_effect = Exception("timeout")
        client = HTTPPaymentClient("fake-url")
        # When/Then lança exceção
        with pytest.raises(Exception):
            client.request_payment(order_id=1, amount=10)

    @patch("src.adapters.gateways.http_payment_client.get_ssm_client")
    @patch("src.adapters.gateways.http_payment_client.requests.post")
    def test_request_payment_invalid_response(self, mock_post, mock_ssm):
        # Mock SSM client
        mock_ssm_client = MagicMock()
        mock_ssm_client.get_parameter.return_value = None
        mock_ssm.return_value = mock_ssm_client
        # Given resposta inválida
        mock_post.return_value.status_code = 500
        mock_post.return_value.ok = False
        mock_post.return_value.text = "error"
        client = HTTPPaymentClient("fake-url")
        # When/Then trata erro
        with pytest.raises(Exception):
            client.request_payment(order_id=1, amount=10)
