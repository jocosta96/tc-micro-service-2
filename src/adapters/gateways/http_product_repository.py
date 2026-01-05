import os
from typing import List, Optional

import requests

from src.application.repositories.product_repository import ProductRepository
from src.entities.product import Product, ProductCategory
from src.entities.value_objects.sku import SKU


class HTTPProductRepository(ProductRepository):
    """HTTP client to fetch product data from the catalog service."""

    def __init__(self, base_url: Optional[str] = None, timeout: int = 5):
        self.base_url = base_url or os.getenv("CATALOG_API_HOST")
        self.timeout = timeout

    def _get(self, path: str):
        if not self.base_url:
            raise ValueError("CATALOG_API_HOST is not configured")

        url = f"http://{self.base_url}{path}"
        try:
            resp = requests.get(url, timeout=self.timeout)
        except Exception as exc:
            raise ValueError(f"Failed to reach catalog service: {exc}") from exc

        if resp.status_code == 404:
            return None
        if not resp.ok:
            raise ValueError(f"Catalog service returned {resp.status_code} for {url}")
        return resp.json()

    def find_by_id(self, product_internal_id: int, include_inactive: bool = False) -> Optional[Product]:
        data = self._get(f"/product/by-id/{product_internal_id}?include_inactive={str(include_inactive).lower()}")
        if not data:
            return None
        return Product(**data)

    # The remaining methods are not used by the order service; explicit stubs keep the interface compliant.
    def save(self, product: Product) -> Product:  # pragma: no cover - not used in order-service
        raise NotImplementedError("Saving products is handled by the catalog service.")

    def find_by_sku(self, sku: SKU, include_inactive: bool = False) -> Optional[Product]:  # pragma: no cover
        raise NotImplementedError("Product lookups by SKU are not implemented in the order service.")

    def find_all(self, include_inactive: bool = False) -> List[Product]:  # pragma: no cover
        raise NotImplementedError("Listing products is handled by the catalog service.")

    def delete(self, product_internal_id: int) -> bool:  # pragma: no cover
        raise NotImplementedError("Product deletion is handled by the catalog service.")

    def exists_by_sku(self, sku: SKU, include_inactive: bool = False) -> bool:  # pragma: no cover
        raise NotImplementedError()

    def exists_by_id(self, product_internal_id: int, include_inactive: bool = False) -> bool:  # pragma: no cover
        raise NotImplementedError()

    def exists_by_name(self, name: str, include_inactive: bool = False) -> bool:  # pragma: no cover
        raise NotImplementedError()

    def exists_by_category(self, category: ProductCategory, include_inactive: bool = False) -> bool:  # pragma: no cover
        raise NotImplementedError()
