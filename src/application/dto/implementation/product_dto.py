from dataclasses import dataclass
from typing import Any, Optional
from src.application.dto.interfaces.request_interface import RequestInterface
from src.application.dto.interfaces.response_interface import ResponseInterface
from src.entities.product import Product, ProductReceiptItem

@dataclass
class ProductCreateRequest(RequestInterface):
    """DTO for product creation request"""

    name: str
    price: float
    category: str
    sku: str
    default_ingredient: list[ProductReceiptItem]

    def to_dict(self):
        return {
            "name": self.name,
            "price": self.price,
            "category": self.category,
            "sku": self.sku,
            "default_ingredient": self.default_ingredient,
        }

@dataclass
class ProductUpdateRequest(RequestInterface):
    """DTO for product update request"""

    internal_id: int
    name: str
    price: float
    category: str
    sku: str
    default_ingredient: list[ProductReceiptItem]

    def to_dict(self):
        return {
            "internal_id": self.internal_id,
            "name": self.name,
            "price": self.price,
            "category": self.category,
            "sku": self.sku,
            "default_ingredient": self.default_ingredient,
        }

@dataclass
class ProductResponse(ResponseInterface):
    """DTO for product response"""

    internal_id: Optional[int]
    name: str
    price: float
    category: str
    sku: str
    is_active: bool
    default_ingredient: list[dict]

    def to_dict(self):
        return {
            "internal_id": self.internal_id,
            "name": self.name,
            "price": self.price,
            "category": self.category,
            "sku": self.sku,
            "is_active": self.is_active,
            "default_ingredient": self.default_ingredient,
        }

    @classmethod
    def from_entity(cls, entity: Product) -> "ProductResponse":
        """Create DTO from entity"""
        # Convert ProductReceiptItem objects to serializable dictionaries
        default_ingredients = []
        for item in entity.default_ingredient:
            default_ingredients.append({
                "ingredient_internal_id": item.ingredient.internal_id,
                "ingredient_name": item.ingredient.name.value,
                "quantity": item.quantity
            })
        
        return cls(
            internal_id=entity.internal_id,
            name=entity.name.value,
            price=float(entity.price.amount),
            category=entity.category.value,
            sku=entity.sku.value,
            is_active=entity.is_active,
            default_ingredient=default_ingredients,
        )

@dataclass
class ProductListResponse(ResponseInterface):
    """DTO for product list response"""

    products: list[ProductResponse]
    total_count: int

    def to_dict(self):
        return {
            "products": [product.to_dict() for product in self.products],
            "total_count": self.total_count,
        }

    @classmethod
    def from_entity(cls, entity: Any) -> "ProductListResponse":
        """Create DTO from entity"""
        return cls(
            products=[ProductResponse.from_entity(product) for product in entity],
            total_count=len(entity),
        )

