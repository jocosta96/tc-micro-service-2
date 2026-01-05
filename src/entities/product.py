from dataclasses import dataclass
from typing import Optional
from enum import Enum

from src.entities.value_objects.name import Name
from src.entities.value_objects.money import Money
from src.entities.ingredient import Ingredient
from src.entities.value_objects.sku import SKU


class ProductCategory(str, Enum):
    BURGER = "burger"
    SIDE = "side"
    DRINK = "drink"
    DESSERT = "dessert"


class ProductReceiptItem:
    def __init__(self, ingredient: Ingredient, quantity: int):
        self.ingredient = ingredient
        self.quantity = quantity
    def __tuple__(self):
        return self.ingredient, self.quantity


@dataclass
class Product:
    """
    Product entity that represents a product in the ordering system.

    This is an entity because:
    - It has an identity (id)
    - It can change over time while maintaining its identity
    - It contains business logic and rules
    - It's the aggregate root for customer-related operations
    """

    name: Name
    price: Money
    category: ProductCategory
    sku: SKU
    default_ingredient: list[ProductReceiptItem]
    is_active: bool
    internal_id: Optional[int] = None


    def __post_init__(self):
        """Validate business rules during object creation"""
        self._validate_business_rules() 

    def _validate_business_rules(self):
        """Validate domain business rules"""

        if not self.name:
            raise ValueError("Product must have a name")
        
        if not self.price:
            raise ValueError("Product must have a price")
        
        if not self.category:
            raise ValueError("Product must have a category")
        
        if not self.sku:
            raise ValueError("Product must have a SKU")
        
        if not self.default_ingredient:
            raise ValueError("Product must have a default ingredient")

        if self.category not in ProductCategory:
            raise ValueError("Product must have a valid category")
        
        for ingredient in self.default_ingredient:
            if self.category == ProductCategory.BURGER:
                if not ingredient.ingredient.applies_to_burger:
                    raise ValueError("Ingredient must apply to burger")
            elif self.category == ProductCategory.SIDE:
                if not ingredient.ingredient.applies_to_side:
                    raise ValueError("Ingredient must apply to side")
            elif self.category == ProductCategory.DRINK:
                if not ingredient.ingredient.applies_to_drink:
                    raise ValueError("Ingredient must apply to drink")
            elif self.category == ProductCategory.DESSERT:
                if not ingredient.ingredient.applies_to_dessert:
                    raise ValueError("Ingredient must apply to dessert")

    def __str__(self) -> str:
        return f"Product(internal_id={self.internal_id}, name={self.name}, price={self.price}, category={self.category}, sku={self.sku}, default_ingredient={self.default_ingredient})"

    def __repr__(self) -> str:
        return f"Product(internal_id={self.internal_id}, name={self.name}, price={self.price}, category={self.category}, sku={self.sku}, default_ingredient={self.default_ingredient})" 

    @classmethod
    def create(
        cls,
        name: str,
        price: Money,
        category: ProductCategory,
        sku: SKU,
        default_ingredient: list[ProductReceiptItem],
        is_active: bool,

        internal_id: Optional[int] = None
    ) -> "Product":

        """Factory method to create an Product"""
        return cls(
            name=Name.create(name),
            price=price,
            category=category,
            sku=sku,
            default_ingredient=default_ingredient,
            is_active=is_active,
            internal_id=internal_id
        )

    @classmethod
    def create_registered(
        cls,
        name: str,
        price: float,
        category: str,
        sku: str,
        default_ingredient: list[ProductReceiptItem],

    ) -> "Product":
        """Factory method to create a registered product from DTO data"""
        return cls.create(
            name=name,
            price=Money(amount=price),
            category=ProductCategory(category),
            sku=SKU.create(sku),
            default_ingredient=default_ingredient,
            is_active=True
        )

    def update(
        self,
        name: str,
        price: float,
        category: str,
        sku: str,
        default_ingredient: list[ProductReceiptItem]
    ) -> None:
        """Update product attributes"""
        self.name = Name.create(name)
        self.price = Money(amount=price)
        self.category = ProductCategory(category)
        self.sku = SKU.create(sku)
        self.default_ingredient = default_ingredient
        # Re-validate business rules after update
        self._validate_business_rules()
