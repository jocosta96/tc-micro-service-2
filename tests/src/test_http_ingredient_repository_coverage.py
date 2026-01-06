from unittest.mock import patch
from src.adapters.gateways.http_ingredient_repository import HTTPIngredientRepository


class TestHTTPIngredientRepository:
    @patch("src.adapters.gateways.http_ingredient_repository.requests.get")
    def test_find_by_id_success(self, mock_get):
        # Given ingrediente existe
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "name": "Tomato",
            "price": {"amount": 1.0},
            "is_active": True,
            "type": "vegetable",
            "applies_to_burger": True,
            "applies_to_side": False,
            "applies_to_drink": False,
            "applies_to_dessert": False,
        }
        repo = HTTPIngredientRepository("fake-url")
        # When buscar
        resp = repo.find_by_id(1)
        # Then retorna objeto Ingredient
        assert str(resp.name) == "Tomato"

    @patch("src.adapters.gateways.http_ingredient_repository.requests.get")
    def test_find_by_id_http_error(self, mock_get):
        # Given erro HTTP
        mock_get.return_value.status_code = 404
        repo = HTTPIngredientRepository("fake-url")
        # When buscar, Then retorna None
        resp = repo.find_by_id(1)
        assert resp is None

    @patch("src.adapters.gateways.http_ingredient_repository.requests.get")
    def test_find_by_id_empty_response(self, mock_get):
        # Given resposta vazia
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = None
        repo = HTTPIngredientRepository("fake-url")
        # When buscar, Then retorna None
        resp = repo.find_by_id(1)
        assert resp is None
