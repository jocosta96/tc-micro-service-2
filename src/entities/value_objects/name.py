from dataclasses import dataclass
import re

from src.config.app_config import app_config


@dataclass(frozen=True)
class Name:
    """
    Name value object that represents a valid Name.

    This is a value object because:
    - It's immutable (frozen=True)
    - It validates itself during creation
    - It has no identity, only value
    - Two emails are equal if they have the same value
    """

    value: str

    def __post_init__(self):
        """Validate the name during object creation"""
        if not self._is_valid_name(self.value):
            raise ValueError(f"Invalid Name: {self.value}")

    @staticmethod
    def _is_valid_name(name: str) -> bool:
        """Validate name format"""
        if not name or name.strip() == "":
            return False
        if (
            len(name.strip()) < app_config.min_name_length
            or len(name.strip()) > app_config.max_name_length
        ):
            return False
        # Check if name contains only letters, spaces, and common name characters
        pattern = r"^[a-zA-ZÀ-ÿ\s\'-]+$"
        return bool(re.match(pattern, name.strip()))

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"Name('{self.value}')"

    @classmethod
    def create(cls, name: str) -> "Name":
        """Factory method to create a Name value object"""
        normalized_name = name.strip().title()  # title() capitalizes each word properly
        return cls(normalized_name)
