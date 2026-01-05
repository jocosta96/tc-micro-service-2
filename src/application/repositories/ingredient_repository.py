from abc import ABC, abstractmethod
from typing import List, Optional

from src.entities.ingredient import Ingredient, IngredientType
from src.entities.product import ProductCategory


class IngredientRepository(ABC):
    """
    Repository interface for Ingredient entity.

    In Clean Architecture:
    - This is part of the Application Business Rules layer
    - It defines the contract for ingredient data access
    - It's implemented by Interface Adapters layer
    - It's used by Use Cases in the Application layer
    """

    @abstractmethod
    def save(self, ingredient: Ingredient) -> Ingredient:
        """Save a ingredient and return the saved ingredient with ID"""
        pass

    @abstractmethod
    def find_by_id(self, ingredient_internal_id: int, include_inactive: bool = False) -> Optional[Ingredient]:
        """Find a ingredient by ID"""
        pass

    @abstractmethod
    def find_by_name(self, name: str, include_inactive: bool = False) -> Optional[Ingredient]:
        """Find a ingredient by name"""
        pass

    @abstractmethod
    def find_by_type(self, type: IngredientType, include_inactive: bool = False) -> List[Ingredient]:
        """Find ingredients by type"""
        pass

    @abstractmethod
    def find_by_applies_usage(
        self,
        category: ProductCategory,
        include_inactive: bool = False
    ) -> List[Ingredient]:
        """Find ingredients by applies_to_burger, applies_to_side, applies_to_drink and applies_to_dessert"""
        pass

    @abstractmethod
    def find_all(self, include_inactive: bool = False) -> List[Ingredient]:
        """Find all ingredients"""
        pass

    @abstractmethod
    def delete(self, ingredient_internal_id: int) -> bool:
        """Soft delete a ingredient by ID (set is_active to False), return True if deleted"""
        pass

    @abstractmethod
    def exists_by_name(self, name: str, include_inactive: bool = False) -> bool:
        """Check if an ingredient exists with the given name"""
        pass

    @abstractmethod
    def exists_by_type(self, type: IngredientType, include_inactive: bool = False) -> bool:
        """Check if an ingredient exists with the given type"""
        pass