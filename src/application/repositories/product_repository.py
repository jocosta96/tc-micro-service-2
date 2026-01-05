from abc import ABC, abstractmethod
from typing import List, Optional
from src.entities.product import Product, ProductCategory
from src.entities.value_objects.sku import SKU

class ProductRepository(ABC):
    """
    Repository interface for Product entity.
    """

    @abstractmethod
    def save(self, product: Product) -> Product:
        """Save a product and return the saved product with ID"""
        pass

    @abstractmethod
    def find_by_id(self, product_internal_id: int, include_inactive: bool = False) -> Optional[Product]:
        """Find a product by internal ID"""
        pass

    @abstractmethod
    def find_by_sku(self, sku: SKU, include_inactive: bool = False) -> Optional[Product]:
        """Find a product by SKU"""
        pass

    @abstractmethod
    def find_all(self, include_inactive: bool = False) -> List[Product]:
        """Find all products"""
        pass

    @abstractmethod
    def delete(self, product_internal_id: int) -> bool:
        """Soft delete a product by ID (set is_active to False), return True if deleted"""
        pass

    @abstractmethod
    def exists_by_sku(self, sku: SKU, include_inactive: bool = False) -> bool:
        """Check if a product exists by SKU"""
        pass

    @abstractmethod
    def exists_by_id(self, product_internal_id: int, include_inactive: bool = False) -> bool:
        """Check if a product exists by internal ID"""
        pass

    @abstractmethod
    def exists_by_name(self, name: str, include_inactive: bool = False) -> bool:
        """Check if a product exists by name"""
        pass

    @abstractmethod
    def exists_by_category(self, category: ProductCategory, include_inactive: bool = False) -> bool:
        """Check if a product exists by category"""
        pass