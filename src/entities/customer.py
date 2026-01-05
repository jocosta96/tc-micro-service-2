from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from .value_objects.document import Document
from .value_objects.email import Email
from .value_objects.name import Name


@dataclass
class Customer:
    """
    Customer entity that represents a customer in the ordering system.

    This is an entity because:
    - It has an identity (id)
    - It can change over time while maintaining its identity
    - It contains business logic and rules
    - It's the aggregate root for customer-related operations
    """

    first_name: Name
    last_name: Name
    email: Email
    document: Document
    is_active: bool
    is_anonymous: bool
    internal_id: Optional[int] = None
    created_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate business rules during object creation"""
        if self.created_at is None:
            self.created_at = datetime.now()
        self._validate_business_rules()

    def _validate_business_rules(self):
        """Validate domain business rules"""
        from src.config.app_config import app_config

        # Rule: Active anonymous customers must have anonymous email
        # Inactive customers can have any email
        if (
            self.is_anonymous
            and not self.email.value == app_config.anonymous_email
            and self.is_active  # Only apply this rule to active customers
        ):
            raise ValueError("Anonymous customers must have anonymous email")

        # Rule: Active registered customers must have both document and email
        # Exception: Inactive registered customers can have empty documents
        if not self.is_anonymous and self.email.value == "" and self.is_active:
            raise ValueError("Registered customers must have an email")

    def soft_delete(self) -> None:
        """Business rule: Soft delete the customer by replacing data with placeholder values"""
        if not self.is_active:
            raise ValueError("Cannot soft delete inactive customer")
        
        # Business rule: Cannot soft delete customer without ID
        if not self.internal_id:
            raise ValueError("Cannot soft delete customer without ID")
            
        # Business rule: Cannot delete active anonymous customers
        # But allow deleting inactive anonymous customers (already soft-deleted)
        if self.is_anonymous and self.is_active:
            raise ValueError("Cannot delete anonymous customer")
            
        # Business rule: Set is_active to False
        self.is_active = False
        
        # Business rule: Replace data with placeholder values for privacy
        self.first_name = Name.create("Deleted")
        self.last_name = Name.create("Customer")
        self.document = Document.create("")
        
        # Business rule: Soft-deleted customers get unique email but remain registered
        self.email = Email.create(f"deleted.{self.internal_id}@fastfood.local")
        # Keep is_anonymous as False - soft-deleted customers remain registered

    @property
    def full_name(self) -> str:
        """Get the customer's full name"""
        return f"{self.first_name.value} {self.last_name.value}".strip()

    @property
    def is_registered(self) -> bool:
        """Check if this customer is registered (not anonymous)"""
        return not self.is_anonymous

    def can_place_order(self) -> bool:
        """Business rule: Check if customer can place an order"""
        # Customer must be active to place orders
        if not self.is_active:
            return False
            
        # Active anonymous customers can always place orders
        if self.is_anonymous:
            return True

        # Active registered customers must have valid email and document
        return not self.email.value == "" and not self.document.is_empty

    def get_display_name(self) -> str:
        """Get display name for UI purposes"""
        if self.is_anonymous:
            return "Anonymous Customer"
        return self.full_name

    def __str__(self) -> str:
        return f"Customer(internal_id={self.internal_id}, name='{self.full_name}', email='{self.email}', is_active={self.is_active})"

    def __repr__(self) -> str:
        return f"Customer(internal_id={self.internal_id}, first_name={self.first_name}, last_name={self.last_name}, email={self.email}, document={self.document}, is_active={self.is_active})"

    @classmethod
    def create_anonymous(cls, internal_id: Optional[int] = None) -> "Customer":
        """Factory method to create an anonymous customer"""
        from src.config.app_config import app_config

        return cls(
            first_name=Name.create("Anonymous"),
            last_name=Name.create("Customer"),
            email=Email.create(app_config.anonymous_email),
            document=Document.create(""),
            is_active=True,
            is_anonymous=True,
            internal_id=internal_id,
        )

    @classmethod
    def create_registered(
        cls,
        first_name: str,
        last_name: str,
        email: str,
        document: str,

        internal_id: Optional[int] = None,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
    ) -> "Customer":
        """Factory method to create a registered customer"""
        return cls(
            first_name=Name.create(first_name),
            last_name=Name.create(last_name),
            email=Email.create(email),
            document=Document.create(document),
            is_active=is_active,
            is_anonymous=False,
            internal_id=internal_id,
            created_at=created_at,
        )
