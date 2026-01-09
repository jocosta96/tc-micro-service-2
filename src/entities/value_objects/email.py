from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Email:
    """
    Email value object that represents a valid email address.

    This is a value object because:
    - It's immutable (frozen=True)
    - It validates itself during creation
    - It has no identity, only value
    - Two emails are equal if they have the same value
    """

    value: str

    def __post_init__(self):
        """Validate the email during object creation"""
        if not self._is_valid_email(self.value):
            raise ValueError(f"Invalid email address: {self.value}")

    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Validate email format using regex"""
        # Allow empty emails for testing and anonymous customers
        if not email or email.strip() == "":
            return True

        # Basic email regex pattern
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"Email('{self.value}')"

    @classmethod
    def create(cls, email: str) -> "Email":
        """Factory method to create an Email value object"""
        return cls(email.strip().lower())

    @property
    def domain(self) -> str:
        """Extract the domain part of the email"""
        if not self.value or "@" not in self.value:
            return ""
        return self.value.split("@")[1]

    @property
    def local_part(self) -> str:
        """Extract the local part of the email"""
        if not self.value or "@" not in self.value:
            return ""
        return self.value.split("@")[0]
