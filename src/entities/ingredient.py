from dataclasses import dataclass
from typing import Optional
from enum import Enum

from src.entities.value_objects.name import Name
from src.entities.value_objects.money import Money


class IngredientType(str, Enum):

    BREAD = "bread"
    MEAT = "meat"
    CHEESE = "cheese"
    VEGETABLE = "vegetable"
    SALAD = "salad"
    SAUCE = "sauce"
    ICE = "ice"
    MILK = "milk"
    TOPPING = "topping"


@dataclass
class Ingredient:
    """
    Ingredient entity that represents a ingredient in the ordering system.

    This is an entity because:
    - It has an identity (id)
    - It can change over time while maintaining its identity
    - It contains business logic and rules
    - It's the aggregate root for customer-related operations
    """

    name: Name
    price: Money
    is_active: bool
    type: IngredientType
    applies_to_burger: bool
    applies_to_side: bool
    applies_to_drink: bool
    applies_to_dessert: bool
    internal_id: Optional[int] = None

    def __post_init__(self):
        """Validate business rules during object creation"""
        self._validate_business_rules()

    def _validate_business_rules(self):
        """Validate domain business rules"""
        # Rule: Ingredient must have a name
        if not self.name:
            raise ValueError("Ingredient must have a name")
        
        # Rule: Ingredient must have a price
        if not self.price:
            raise ValueError("Ingredient must have a price")

        # Rule: Ingredient must have a type
        if not self.type:
            raise ValueError("Ingredient must have a type")
        
        # Rule: Ingredient must have an usage
        if not (
            self.applies_to_burger or  
            self.applies_to_side or 
            self.applies_to_drink or 
            self.applies_to_dessert
        ):
            raise ValueError("Ingredient must have an applies_to")

        if self.applies_to_burger and self.type not in [
            IngredientType.BREAD,
            IngredientType.MEAT,
            IngredientType.CHEESE,
            IngredientType.VEGETABLE,
            IngredientType.SALAD,
            IngredientType.SAUCE
        ]:
            raise ValueError("Ingredient must be a valid burger ingredient")
        
        if self.applies_to_side and self.type not in [
            IngredientType.SALAD,
            IngredientType.SAUCE,
            IngredientType.VEGETABLE,
        ]:
            raise ValueError("Ingredient must be a valid side ingredient")
        
        if self.applies_to_drink and self.type not in [
            IngredientType.ICE,
            IngredientType.MILK
        ]:
            raise ValueError("Ingredient must be a valid drink ingredient")
        
        if self.applies_to_dessert and self.type not in [
            IngredientType.TOPPING,
        ]:
            raise ValueError("Ingredient must be a valid dessert ingredient")

    def __str__(self) -> str:
        return f"Ingredient(internal_id={self.internal_id}, name={self.name}, price={self.price}, is_active={self.is_active})"

    def __repr__(self) -> str:
        return f"Ingredient(internal_id={self.internal_id}, name={self.name}, price={self.price}, is_active={self.is_active})" 

    @classmethod
    def create(
        cls,
        name: str,
        price: Money,
        is_active: bool,
        type: IngredientType,
        applies_to_burger: bool,
        applies_to_side: bool,
        applies_to_drink: bool,
        applies_to_dessert: bool,

        internal_id: Optional[int] = None
    ) -> "Ingredient":

        """Factory method to create an Ingredient"""
        return cls(
            name=Name.create(name),
            price=price,
            is_active=is_active,
            type=type,
            applies_to_burger=applies_to_burger,
            applies_to_side=applies_to_side,
            applies_to_drink=applies_to_drink,
            applies_to_dessert=applies_to_dessert,
            internal_id=internal_id
        )
