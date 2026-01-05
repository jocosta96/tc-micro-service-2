from dataclasses import dataclass
from typing import Optional, Any
from src.entities.ingredient import IngredientType
from src.application.dto.interfaces.request_interface import RequestInterface
from src.application.dto.interfaces.response_interface import ResponseInterface

@dataclass
class IngredientCreateRequest(RequestInterface):
    """DTO for ingredient creation request"""

    name: str
    price: float
    is_active: bool
    type: IngredientType
    applies_to_burger: bool
    applies_to_side: bool
    applies_to_drink: bool
    applies_to_dessert: bool

    def to_dict(self):
        return {
            "name": self.name,
            "price": self.price,
            "is_active": self.is_active,
            "type": self.type,
            "applies_to_burger": self.applies_to_burger,
            "applies_to_side": self.applies_to_side,
            "applies_to_drink": self.applies_to_drink,
            "applies_to_dessert": self.applies_to_dessert,
        }

@dataclass
class IngredientUpdateRequest(RequestInterface):
    """DTO for ingredient update request"""

    internal_id: int
    name: str
    price: float
    is_active: bool
    type: IngredientType
    applies_to_burger: bool
    applies_to_side: bool
    applies_to_drink: bool
    applies_to_dessert: bool

    def to_dict(self):
        return {
            "internal_id": self.internal_id,
            "name": self.name,
            "price": self.price,
            "is_active": self.is_active,
            "type": self.type,
            "applies_to_burger": self.applies_to_burger,
            "applies_to_side": self.applies_to_side,
            "applies_to_drink": self.applies_to_drink,
            "applies_to_dessert": self.applies_to_dessert,
        }

@dataclass
class IngredientResponse(ResponseInterface):
    """DTO for ingredient response"""

    internal_id: Optional[int]
    name: str
    price: float
    is_active: bool
    type: IngredientType
    applies_to_burger: bool
    applies_to_side: bool
    applies_to_drink: bool
    applies_to_dessert: bool

    @classmethod
    def from_entity(cls, ingredient):
        """Create DTO from Ingredient entity"""
        return cls(
            internal_id=ingredient.internal_id,
            name=ingredient.name.value,
            price=float(ingredient.price.amount),
            is_active=ingredient.is_active,
            type=ingredient.type,
            applies_to_burger=ingredient.applies_to_burger,
            applies_to_side=ingredient.applies_to_side,
            applies_to_drink=ingredient.applies_to_drink,
            applies_to_dessert=ingredient.applies_to_dessert,
        )

    def to_dict(self):
        return {
            "internal_id": self.internal_id,
            "name": self.name,
            "price": self.price,
            "is_active": self.is_active,
            "type": self.type,
            "applies_to_burger": self.applies_to_burger,
            "applies_to_side": self.applies_to_side,
            "applies_to_drink": self.applies_to_drink,
            "applies_to_dessert": self.applies_to_dessert,
        }

@dataclass
class IngredientListResponse(ResponseInterface):
    """DTO for ingredient list response"""

    ingredients: list[IngredientResponse]
    total_count: int

    def to_dict(self):
        return {
            "ingredients": [ingredient.to_dict() for ingredient in self.ingredients],
            "total_count": self.total_count,
        }

    @classmethod
    def from_entity(cls, entity: Any) -> "IngredientListResponse":
        """Create DTO from entity"""
        return cls(
            ingredients=[IngredientResponse.from_entity(ingredient) for ingredient in entity.ingredients],
            total_count=entity.total_count,
        )
