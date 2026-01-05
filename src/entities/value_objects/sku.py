from dataclasses import dataclass
import re


@dataclass(frozen=True)
class SKU:
    """
    SKU value object that represents a valid SKU.

    This is a value object because:
    - It's immutable (frozen=True)
    - It validates itself during creation
    - It has no identity, only value
    - Two SKUs are equal if they have the same value
    """

    value: str

    def __post_init__(self):
        """Validate the SKU during object creation"""
        if not self._is_valid_sku(self.value):
            raise ValueError(f"Invalid SKU: {self.value}")

    @staticmethod
    def _is_valid_sku(values: str) -> bool:
        """Validate SKU format"""

        if not (len(values) > 8 and len(values) < 15):
            return False

        format_pattern = r"^[A-Za-z]+-\d{4}-[A-Za-z]{3}$"
        if not re.match(format_pattern, values):
            return False
        
        return True

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"SKU('{self.value}')"

    @classmethod
    def create(cls, sku: str) -> "SKU":
        """Factory method to create a SKU value object"""
        normalized_sku = sku.strip().upper()
        return cls(normalized_sku)
