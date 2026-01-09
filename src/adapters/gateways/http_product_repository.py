import os
from typing import List, Optional

import requests

from src.application.repositories.product_repository import ProductRepository
from src.entities.product import Product, ProductCategory, ProductReceiptItem
from src.entities.ingredient import Ingredient
from src.entities.value_objects.sku import SKU
from src.entities.value_objects.money import Money
from src.config.aws_ssm import get_ssm_client

class HTTPProductRepository(ProductRepository):
    """HTTP client to fetch product data from the catalog service."""

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
        print(url)
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
            ingredient_type = mapped.get("type", "")
            mapped["applies_to_burger"] = ingredient_type in ["bread", "meat", "cheese", "vegetable", "salad", "sauce"]
            mapped["applies_to_side"] = ingredient_type in ["salad", "sauce", "vegetable"]
            mapped["applies_to_drink"] = ingredient_type in ["ice", "milk"]
            mapped["applies_to_dessert"] = ingredient_type in ["topping"]
        
        return mapped

    def find_by_id(
        self, product_internal_id: int, include_inactive: bool = False
    ) -> Optional[Product]:
        data = self._get(
            f"/product/by-id/{product_internal_id}?include_inactive={str(include_inactive).lower()}"
        )
        if not data:
            return None
        
        # Convert price
        if "price" in data and not isinstance(data["price"], Money):
            if isinstance(data["price"], (int, float)):
                data["price"] = Money(amount=data["price"])
            elif isinstance(data["price"], dict) and "amount" in data["price"]:
                data["price"] = Money(**data["price"])
        
        # Convert default_ingredient
        default_ingredients = []
        for ing_data in data.get("default_ingredient", []):
            ingredient_response = self._get(
                f"/ingredient/by-id/{ing_data.get('ingredient_internal_id')}?include_inactive=false"
            )
            if ingredient_response:
                ingredient_response = self._map_ingredient_fields(ingredient_response)
                ingredient_obj = Ingredient(**ingredient_response)
                default_ingredients.append(
                    ProductReceiptItem(
                        ingredient=ingredient_obj,
                        quantity=ing_data.get("quantity", 1)
                    )
                )
        data["default_ingredient"] = default_ingredients
        
        return Product(**data)

    # The remaining methods are not used by the order service; explicit stubs keep the interface compliant.
    def save(
        self, product: Product
    ) -> Product:  # pragma: no cover - not used in order-service
        raise NotImplementedError("Saving products is handled by the catalog service.")

    def find_by_sku(
        self, sku: SKU, include_inactive: bool = False
    ) -> Optional[Product]:  # pragma: no cover
        raise NotImplementedError(
            "Product lookups by SKU are not implemented in the order service."
        )

    def find_all(
        self, include_inactive: bool = False
    ) -> List[Product]:  # pragma: no cover
        raise NotImplementedError("Listing products is handled by the catalog service.")

    def delete(self, product_internal_id: int) -> bool:  # pragma: no cover
        raise NotImplementedError("Product deletion is handled by the catalog service.")

    def exists_by_sku(
        self, sku: SKU, include_inactive: bool = False
    ) -> bool:  # pragma: no cover
        raise NotImplementedError()

    def exists_by_id(
        self, product_internal_id: int, include_inactive: bool = False
    ) -> bool:  # pragma: no cover
        raise NotImplementedError()

    def exists_by_name(
        self, name: str, include_inactive: bool = False
    ) -> bool:  # pragma: no cover
        raise NotImplementedError()

    def exists_by_category(
        self, category: ProductCategory, include_inactive: bool = False
    ) -> bool:  # pragma: no cover
        raise NotImplementedError()
