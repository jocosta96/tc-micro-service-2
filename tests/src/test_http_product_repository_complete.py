"""
Comprehensive tests for HTTPProductRepository to increase coverage.
Focuses on find_by_id with various scenarios including 404, network errors, and successful responses.
"""

from unittest.mock import MagicMock, patch
import pytest
import requests

from src.adapters.gateways.http_product_repository import HTTPProductRepository
from src.entities.product import Product


@pytest.fixture
def product_repo():
    """Fixture to create HTTPProductRepository with test base URL"""
    return HTTPProductRepository(base_url="catalog-service.local", timeout=5)


@pytest.fixture
def mock_requests_get():
    """Fixture to mock requests.get"""
    with patch("requests.get") as mock_get:
        yield mock_get


def test_init_with_base_url():
    """Given base_url provided, when repository is initialized, then uses provided URL"""
    repo = HTTPProductRepository(base_url="test.local")

    assert repo.base_url == "test.local"
    assert repo.timeout == 5


def test_init_with_env_url():
    """Given CATALOG_API_HOST env var, when repository is initialized, then uses env var"""
    with patch.dict("os.environ", {"CATALOG_API_HOST": "env-catalog.local"}):
        repo = HTTPProductRepository()

        assert repo.base_url == "env-catalog.local"


def test_init_with_custom_timeout():
    """Given custom timeout, when repository is initialized, then uses custom timeout"""
    repo = HTTPProductRepository(base_url="test.local", timeout=10)

    assert repo.timeout == 10


def test_get_without_base_url():
    """Given no base_url configured, when _get is called, then raises ValueError"""
    repo = HTTPProductRepository(base_url=None)

    with pytest.raises(ValueError) as exc_info:
        repo._get("/product/by-id/1")

    assert "CATALOG_API_HOST is not configured" in str(exc_info.value)


def test_get_uses_https(mock_requests_get, product_repo):
    """Given base URL, when _get is called, then uses HTTPS protocol"""
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.json.return_value = {"internal_id": 1}
    mock_requests_get.return_value = mock_response

    product_repo._get("/product/by-id/1")

    # Verify HTTPS is used
    call_url = mock_requests_get.call_args[0][0]
    assert call_url.startswith("https://")
    assert "catalog-service.local" in call_url


def test_get_returns_none_on_404(mock_requests_get, product_repo):
    """Given resource not found (404), when _get is called, then returns None"""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.ok = False
    mock_requests_get.return_value = mock_response

    result = product_repo._get("/product/by-id/999")

    assert result is None


def test_get_raises_on_non_ok_status(mock_requests_get, product_repo):
    """Given non-OK status (500), when _get is called, then raises ValueError"""
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.ok = False
    mock_requests_get.return_value = mock_response

    with pytest.raises(ValueError) as exc_info:
        product_repo._get("/product/by-id/1")

    assert "returned 500" in str(exc_info.value)


def test_get_raises_on_connection_error(mock_requests_get, product_repo):
    """Given connection error, when _get is called, then raises ValueError"""
    mock_requests_get.side_effect = requests.exceptions.ConnectionError(
        "Connection refused"
    )

    with pytest.raises(ValueError) as exc_info:
        product_repo._get("/product/by-id/1")

    assert "Failed to reach catalog service" in str(exc_info.value)


def test_get_raises_on_timeout(mock_requests_get, product_repo):
    """Given request timeout, when _get is called, then raises ValueError"""
    mock_requests_get.side_effect = requests.exceptions.Timeout("Request timed out")

    with pytest.raises(ValueError) as exc_info:
        product_repo._get("/product/by-id/1")

    assert "Failed to reach catalog service" in str(exc_info.value)


def test_get_success_returns_json(mock_requests_get, product_repo):
    """Given successful response, when _get is called, then returns JSON data"""
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.json.return_value = {"internal_id": 1, "name": "Test Product"}
    mock_requests_get.return_value = mock_response

    result = product_repo._get("/product/by-id/1")

    assert result == {"internal_id": 1, "name": "Test Product"}


def test_find_by_id_found(mock_requests_get, product_repo):
    """Given product exists, when find_by_id is called, then returns Product entity"""
    from src.entities.product import ProductReceiptItem, ProductCategory
    from src.entities.ingredient import Ingredient, IngredientType
    from src.entities.value_objects.name import Name
    from src.entities.value_objects.money import Money
    from src.entities.value_objects.sku import SKU

    # Create actual Ingredient object
    ingredient = Ingredient(
        name=Name.create("Cheese"),
        price=Money(1.0),
        is_active=True,
        type=IngredientType.CHEESE,
        applies_to_burger=True,
        applies_to_side=False,
        applies_to_drink=False,
        applies_to_dessert=False,
    )

    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.json.return_value = {
        "name": Name.create("Test Product"),
        "price": Money(10.0),
        "is_active": True,
        "default_ingredient": [ProductReceiptItem(ingredient, 1)],
        "category": ProductCategory.BURGER,
        "sku": SKU.create("P-1234-ABC"),
        "internal_id": 1,
    }
    mock_requests_get.return_value = mock_response

    result = product_repo.find_by_id(1, include_inactive=False)

    assert result is not None
    assert result.internal_id == 1
    mock_requests_get.assert_called_once()

    # Verify include_inactive parameter is passed
    call_url = mock_requests_get.call_args[0][0]
    assert "include_inactive=false" in call_url


def test_find_by_id_not_found(mock_requests_get, product_repo):
    """Given product does not exist (404), when find_by_id is called, then returns None"""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.ok = False
    mock_requests_get.return_value = mock_response

    result = product_repo.find_by_id(999)

    assert result is None


def test_find_by_id_with_include_inactive(mock_requests_get, product_repo):
    """Given include_inactive=True, when find_by_id is called, then passes parameter correctly"""
    from src.entities.product import ProductReceiptItem, ProductCategory
    from src.entities.ingredient import Ingredient, IngredientType
    from src.entities.value_objects.name import Name
    from src.entities.value_objects.money import Money
    from src.entities.value_objects.sku import SKU

    # Create actual Ingredient object
    ingredient = Ingredient(
        name=Name.create("Lettuce"),
        price=Money(0.5),
        is_active=True,
        type=IngredientType.VEGETABLE,
        applies_to_burger=False,
        applies_to_side=True,
        applies_to_drink=False,
        applies_to_dessert=False,
    )

    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.json.return_value = {
        "name": Name.create("Inactive Product"),
        "price": Money(5.0),
        "is_active": False,
        "default_ingredient": [ProductReceiptItem(ingredient, 1)],
        "category": ProductCategory.SIDE,
        "sku": SKU.create("P-5678-XYZ"),
        "internal_id": 2,
    }
    mock_requests_get.return_value = mock_response

    result = product_repo.find_by_id(2, include_inactive=True)

    assert result is not None
    # Verify include_inactive=true is in URL
    call_url = mock_requests_get.call_args[0][0]
    assert "include_inactive=true" in call_url


def test_find_by_id_connection_error(mock_requests_get, product_repo):
    """Given network error, when find_by_id is called, then raises ValueError"""
    mock_requests_get.side_effect = requests.exceptions.RequestException(
        "Network error"
    )

    with pytest.raises(ValueError) as exc_info:
        product_repo.find_by_id(1)

    assert "Failed to reach catalog service" in str(exc_info.value)


def test_find_by_id_server_error(mock_requests_get, product_repo):
    """Given server error (500), when find_by_id is called, then raises ValueError"""
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.ok = False
    mock_requests_get.return_value = mock_response

    with pytest.raises(ValueError) as exc_info:
        product_repo.find_by_id(1)

    assert "returned 500" in str(exc_info.value)


def test_save_not_implemented(product_repo):
    """Given save is called, when method is invoked, then raises NotImplementedError"""
    from src.entities.value_objects.name import Name
    from src.entities.value_objects.money import Money
    from src.entities.value_objects.sku import SKU
    from src.entities.product import ProductCategory, ProductReceiptItem
    from src.entities.ingredient import Ingredient, IngredientType

    ingredient = Ingredient(
        name=Name.create("Cheese"),
        price=Money(1.0),
        is_active=True,
        type=IngredientType.CHEESE,
        applies_to_burger=True,
        applies_to_side=False,
        applies_to_drink=False,
        applies_to_dessert=False,
    )

    product = Product(
        name=Name.create("Test"),
        price=Money(10.0),
        is_active=True,
        default_ingredient=[ProductReceiptItem(ingredient, 1)],
        category=ProductCategory.BURGER,
        sku=SKU.create("P-1234-ABC"),
    )

    with pytest.raises(NotImplementedError):
        product_repo.save(product)


def test_find_by_sku_not_implemented(product_repo):
    """Given find_by_sku is called, when method is invoked, then raises NotImplementedError"""
    from src.entities.value_objects.sku import SKU

    with pytest.raises(NotImplementedError):
        product_repo.find_by_sku(SKU.create("P-1234-ABC"))


def test_find_all_not_implemented(product_repo):
    """Given find_all is called, when method is invoked, then raises NotImplementedError"""
    with pytest.raises(NotImplementedError):
        product_repo.find_all()


def test_delete_not_implemented(product_repo):
    """Given delete is called, when method is invoked, then raises NotImplementedError"""
    with pytest.raises(NotImplementedError):
        product_repo.delete(1)


def test_exists_by_sku_not_implemented(product_repo):
    """Given exists_by_sku is called, when method is invoked, then raises NotImplementedError"""
    from src.entities.value_objects.sku import SKU

    with pytest.raises(NotImplementedError):
        product_repo.exists_by_sku(SKU.create("P-1234-ABC"))


def test_exists_by_id_not_implemented(product_repo):
    """Given exists_by_id is called, when method is invoked, then raises NotImplementedError"""
    with pytest.raises(NotImplementedError):
        product_repo.exists_by_id(1)


def test_exists_by_name_not_implemented(product_repo):
    """Given exists_by_name is called, when method is invoked, then raises NotImplementedError"""
    with pytest.raises(NotImplementedError):
        product_repo.exists_by_name("Test Product")


def test_exists_by_category_not_implemented(product_repo):
    """Given exists_by_category is called, when method is invoked, then raises NotImplementedError"""
    from src.entities.product import ProductCategory

    with pytest.raises(NotImplementedError):
        product_repo.exists_by_category(ProductCategory.BURGER)
