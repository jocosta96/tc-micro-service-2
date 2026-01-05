from decimal import Decimal, ROUND_HALF_EVEN
from typing import Union
from dataclasses import dataclass


@dataclass(frozen=False)
class Money:
    """
    Money value object that represents a valid monetary amount.

    This is a value object because:
    - It's mutable 
    - It validates itself during creation
    - It has no identity, only value
    - Two money objects are equal if they have the same amount
    """

    amount: Decimal

    def __post_init__(self):
        """Validate the money amount during object creation"""
        # Convert float to Decimal if needed
        if isinstance(self.amount, float):
            self.amount = Decimal(str(self.amount))
        
        if not self._is_valid_amount(self.amount):
            raise ValueError(f"Invalid amount: {self.amount}")

    @staticmethod
    def _is_valid_amount(amount: Decimal) -> bool:
        """
        Validates the money amount:
        1. Must be non-negative
        2. Must have at most 2 decimal places
        """            
        # Check if amount is negative
        if amount < 0:
            return False
            
        normalized = amount.normalize()
        decimal_places = -normalized.as_tuple().exponent if normalized.as_tuple().exponent < 0 else 0
        if decimal_places > 2:
            return False
            
        return True

    def __str__(self) -> str:
        return str(self._format(self.amount))

    def __repr__(self) -> str:
        return f"Money(amount='{self._format(self.amount)}')"

    @classmethod
    def create(cls, amount: Decimal) -> "Money":
        """Factory method to create a Money value object"""
        return cls(amount=amount)

    @staticmethod
    def _format(value: Decimal) -> Decimal:
        """Formats the amount to 2 decimal places"""
        return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)

    @property 
    def value(self) -> float:
        """Get the amount as a float"""
        return float(self._format(self.amount))

    def __add__(self, other: Union["Money", Decimal]) -> "Money":
        """Add two money objects or a money object and a decimal"""
        if isinstance(other, Decimal):
            other = Money(amount=other)
        return Money(amount=self.amount + other.amount)




