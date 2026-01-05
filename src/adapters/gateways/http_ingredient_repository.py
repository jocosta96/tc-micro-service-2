import os
from typing import List, Optional

import requests

from src.application.repositories.ingredient_repository import IngredientRepository
from src.entities.ingredient import Ingredient, IngredientType
from src.entities.product import ProductCategory


class HTTPIngredientRepository(IngredientRepository):
    """HTTP client to fetch ingredient data from the catalog service."""

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

    def find_by_id(self, ingredient_internal_id: int, include_inactive: bool = False) -> Optional[Ingredient]:
        data = self._get(f"/ingredient/by-id/{ingredient_internal_id}?include_inactive={str(include_inactive).lower()}")
        if not data:
            return None
        return Ingredient(**data)

    # The remaining methods are not used by the order service; explicit stubs keep the interface compliant.
    def save(self, ingredient: Ingredient) -> Ingredient:  # pragma: no cover - not used in order-service
        raise NotImplementedError("Saving ingredients is handled by the catalog service.")

    def find_by_name(self, name: str, include_inactive: bool = False) -> Optional[Ingredient]:  # pragma: no cover
        raise NotImplementedError()

    def find_by_type(self, type: IngredientType, include_inactive: bool = False) -> List[Ingredient]:  # pragma: no cover
        raise NotImplementedError()

    def find_by_applies_usage(
        self,
        category: ProductCategory,
        include_inactive: bool = False
    ) -> List[Ingredient]:  # pragma: no cover
        raise NotImplementedError()

    def find_all(self, include_inactive: bool = False) -> List[Ingredient]:  # pragma: no cover
        raise NotImplementedError()

    def delete(self, ingredient_internal_id: int) -> bool:  # pragma: no cover
        raise NotImplementedError()

    def exists_by_name(self, name: str, include_inactive: bool = False) -> bool:  # pragma: no cover
        raise NotImplementedError()

    def exists_by_type(self, type: IngredientType, include_inactive: bool = False) -> bool:  # pragma: no cover
        raise NotImplementedError()
