import os
from typing import List, Optional

import requests

from src.application.repositories.ingredient_repository import IngredientRepository
from src.entities.ingredient import Ingredient, IngredientType
from src.entities.product import ProductCategory
from src.entities.value_objects.money import Money
from src.config.aws_ssm import get_ssm_client


class HTTPIngredientRepository(IngredientRepository):
    """HTTP client to fetch ingredient data from the catalog service."""

    def __init__(self, 
        base_url: Optional[str] = None, 
        timeout: int = 5,
        token: Optional[str] = None
    ):
        self.base_url = get_ssm_client().get_parameter(
            "/ordering-system/catalog/apigateway/url",
            decrypt=True
        )  or \
        base_url or \
        os.getenv("CATALOG_API_HOST")


        self.token = token or \
        get_ssm_client().get_parameter(
            "/ordering-system/catalog/apigateway/token",
            decrypt=True
        )  or \
        os.getenv("CATALOG_API_TOKEN")

        self.timeout = timeout

    def _get(self, path: str):
        if not self.base_url:
            raise ValueError("CATALOG_API_HOST is not configured")

        url = f"{self.base_url}{path}"
        try:
            resp = requests.get(
                url, 
                timeout=self.timeout,
                headers={"Authorization": f"{self.token}"} if self.token else {}
            )
        except Exception as exc:
            raise ValueError(f"Failed to reach catalog service: {exc}") from exc

        if resp.status_code == 404:
            return None
        if not resp.ok:
            raise ValueError(f"Catalog service returned {resp.status_code} for {url}")
        return resp.json()

    def _map_ingredient_fields(self, ingredient_data: dict) -> dict:
        """Map catalog ingredient fields to entity fields"""
        mapped = ingredient_data.copy()
        
        # Convert price
        if "price" in mapped and not isinstance(mapped["price"], Money):
            if isinstance(mapped["price"], (int, float)):
                mapped["price"] = Money(amount=mapped["price"])
            elif isinstance(mapped["price"], dict) and "amount" in mapped["price"]:
                mapped["price"] = Money(**mapped["price"])
        
        # Map appliesto fields
        if "appliesto_burger" in mapped:
            mapped["applies_to_burger"] = mapped.pop("appliesto_burger")
        if "appliesto_side" in mapped:
            mapped["applies_to_side"] = mapped.pop("appliesto_side")
        if "appliesto_drink" in mapped:
            mapped["applies_to_drink"] = mapped.pop("appliesto_drink")
        if "appliesto_dessert" in mapped:
            mapped["applies_to_dessert"] = mapped.pop("appliesto_dessert")
        
        # Infer applies_to from type if missing
        if "applies_to_burger" not in mapped:
            ingredient_type = str(mapped.get("type", "")).lower()
            mapped["applies_to_burger"] = ingredient_type in ["bread", "meat", "cheese", "vegetable", "salad", "sauce"]
            mapped["applies_to_side"] = ingredient_type in ["salad", "sauce", "vegetable"]
            mapped["applies_to_drink"] = ingredient_type in ["ice", "milk"]
            mapped["applies_to_dessert"] = ingredient_type in ["topping"]
        
        return mapped

    def find_by_id(
        self, ingredient_internal_id: int, include_inactive: bool = False
    ) -> Optional[Ingredient]:
        data = self._get(
            f"/ingredient/by-id/{ingredient_internal_id}?include_inactive={str(include_inactive).lower()}"
        )
        if not data:
            return None
        
        data = self._map_ingredient_fields(data)
        return Ingredient(**data)

    # The remaining methods are not used by the order service; explicit stubs keep the interface compliant.
    def save(
        self, ingredient: Ingredient
    ) -> Ingredient:  # pragma: no cover - not used in order-service
        raise NotImplementedError(
            "Saving ingredients is handled by the catalog service."
        )

    def find_by_name(
        self, name: str, include_inactive: bool = False
    ) -> Optional[Ingredient]:  # pragma: no cover
        raise NotImplementedError()

    def find_by_type(
        self, ingredient_type: IngredientType, include_inactive: bool = False
    ) -> List[Ingredient]:  # pragma: no cover
        raise NotImplementedError()

    def find_by_applies_usage(
        self, category: ProductCategory, include_inactive: bool = False
    ) -> List[Ingredient]:  # pragma: no cover
        raise NotImplementedError()

    def find_all(
        self, include_inactive: bool = False
    ) -> List[Ingredient]:  # pragma: no cover
        raise NotImplementedError()

    def delete(self, ingredient_internal_id: int) -> bool:  # pragma: no cover
        raise NotImplementedError()

    def exists_by_name(
        self, name: str, include_inactive: bool = False
    ) -> bool:  # pragma: no cover
        raise NotImplementedError()

    def exists_by_type(
        self, ingredient_type: IngredientType, include_inactive: bool = False
    ) -> bool:  # pragma: no cover
        raise NotImplementedError()
