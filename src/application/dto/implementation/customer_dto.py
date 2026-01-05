from dataclasses import dataclass
from typing import Optional, Any
from datetime import datetime
from src.application.dto.interfaces.request_interface import RequestInterface
from src.application.dto.interfaces.response_interface import ResponseInterface

@dataclass
class CustomerCreateRequest(RequestInterface):
    """DTO for customer creation request"""

    first_name: str
    last_name: str
    email: str
    document: str

    def to_dict(self):
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "document": self.document,
        }

@dataclass
class CustomerUpdateRequest(RequestInterface):
    """DTO for customer update request"""

    internal_id: int
    first_name: str
    last_name: str
    email: str
    document: str

    def to_dict(self):

        return {
            "internal_id": self.internal_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "document": self.document,
        }


@dataclass
class CustomerResponse(ResponseInterface):
    """DTO for customer response"""

    internal_id: Optional[int]
    first_name: str
    last_name: str
    email: str
    document: str
    full_name: str
    is_anonymous: bool
    is_registered: bool
    is_active: bool
    created_at: Optional[datetime]
    
    @classmethod
    def from_entity(cls, customer):
        """Create DTO from Customer entity"""
        return cls(
            internal_id=customer.internal_id,
            first_name=customer.first_name.value,
            last_name=customer.last_name.value,
            email=customer.email.value,
            document=customer.document.value,
            full_name=customer.full_name,
            is_anonymous=customer.is_anonymous,
            is_registered=customer.is_registered,
            is_active=customer.is_active,
            created_at=customer.created_at,
        )

    def to_dict(self):
        return {
            "internal_id": self.internal_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "document": self.document,
            "full_name": self.full_name,
            "is_anonymous": self.is_anonymous,
            "is_registered": self.is_registered,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


@dataclass
class CustomerListResponse(ResponseInterface):
    """DTO for customer list response"""

    customers: list[CustomerResponse]
    total_count: int

    def to_dict(self):
        from datetime import datetime
        return {
            "data": [customer.to_dict() for customer in self.customers],
            "total_count": self.total_count,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    @classmethod
    def from_entity(cls, entity: Any) -> "CustomerListResponse":
        """Create DTO from entity"""
        return cls(
            customers=[CustomerResponse.from_entity(customer) for customer in entity.customers],
            total_count=entity.total_count,
        )
