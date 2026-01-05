from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any

from src.application.dto.interfaces.request_interface import RequestInterface
from src.application.dto.interfaces.response_interface import ResponseInterface
from src.entities.order import Order, OrderItem


@dataclass
class OrderItemRequest(RequestInterface):
    """Request DTO for order item creation"""
    product_internal_id: int
    additional_ingredient_internal_ids: List[int] = None
    remove_ingredient_internal_ids: List[int] = None

    def __post_init__(self):
        if self.additional_ingredient_internal_ids is None:
            self.additional_ingredient_internal_ids = []
        if self.remove_ingredient_internal_ids is None:
            self.remove_ingredient_internal_ids = []

    def to_dict(self) -> dict:
        return {
            "product_internal_id": self.product_internal_id,
            "additional_ingredient_internal_ids": self.additional_ingredient_internal_ids,
            "remove_ingredient_internal_ids": self.remove_ingredient_internal_ids,
        }


@dataclass
class OrderCreateRequest(RequestInterface):
    """Request DTO for order creation"""
    customer_internal_id: int
    order_items: List[OrderItemRequest]

    def to_dict(self) -> dict:
        return {
            "customer_internal_id": self.customer_internal_id,
            "order_items": [item.to_dict() for item in self.order_items],
        }


@dataclass
class OrderUpdateRequest(RequestInterface):
    """Request DTO for order updates"""
    status: Optional[str] = None
    order_items: Optional[List[OrderItemRequest]] = None

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "order_items": [item.to_dict() for item in self.order_items] if self.order_items else None,
        }


@dataclass
class PaymentRequest(RequestInterface):
    """Request DTO for payment processing"""
    transaction_id: str
    approval_status: bool
    date: datetime
    message: str = ""

    def to_dict(self) -> dict:
        return {
            "transaction_id": self.transaction_id,
            "approval_status": self.approval_status,
            "date": self.date.isoformat() if self.date else None,
            "message": self.message,
        }


@dataclass
class PaymentRequestResponse(ResponseInterface):
    """Response DTO for initiating payment request (payment-service)"""
    order_id: int
    amount: float
    transaction_id: str
    payment_url: Optional[str]
    expires_at: Optional[str]

    def to_dict(self) -> dict:
        return {
            "order_id": self.order_id,
            "amount": self.amount,
            "transaction_id": self.transaction_id,
            "payment_url": self.payment_url,
            "expires_at": self.expires_at,
        }

    @classmethod
    def from_entity(cls, entity: Any) -> "PaymentRequestResponse":
        raise NotImplementedError("PaymentRequestResponse is created directly, not from entity")


@dataclass
class OrderItemResponse(ResponseInterface):
    """Response DTO for order item"""
    internal_id: int
    product_internal_id: int
    product_name: str
    product_price: float
    additional_ingredients: List[int]
    remove_ingredients: List[int]
    item_receipt: List[Dict[str, Any]]
    price: float

    def to_dict(self) -> dict:
        return {
            "internal_id": self.internal_id,
            "product_internal_id": self.product_internal_id,
            "product_name": self.product_name,
            "product_price": self.product_price,
            "additional_ingredients": [str(ing) for ing in self.additional_ingredients],
            "remove_ingredients": [str(ing) for ing in self.remove_ingredients],
            "item_receipt": self.item_receipt,
            "price": self.price,
        }

    @classmethod
    def from_entity(cls, order_item: OrderItem) -> "OrderItemResponse":
        """Convert OrderItem entity to OrderItemResponse DTO"""
        return cls(
            internal_id=order_item.internal_id,
            product_internal_id=order_item.product.internal_id,
            product_name=str(order_item.product.name),
            product_price=order_item.product.price.value,
            additional_ingredients=[ing.internal_id for ing in order_item.additional_ingredient],
            remove_ingredients=[ing.internal_id for ing in order_item.remove_ingredient],
            item_receipt=[
                {
                    "ingredient_internal_id": item.ingredient.internal_id,
                    "ingredient_name": str(item.ingredient.name),
                    "quantity": item.quantity
                }
                for item in order_item.get_item_receipt()
            ],
            price=order_item.price.value
        )


@dataclass
class OrderResponse(ResponseInterface):
    """Response DTO for order"""
    internal_id: int
    customer_internal_id: int
    order_items: List[OrderItemResponse]
    value: float
    status: str
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    has_payment_verified: bool
    payment_date: Optional[datetime]
    payment_transaction_id: str
    payment_message: str
    order_display_id: str

    def to_dict(self) -> dict:
        return {
            "internal_id": self.internal_id,
            "customer_internal_id": self.customer_internal_id,
            "order_items": [item.to_dict() for item in self.order_items],
            "value": self.value,
            "status": self.status,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "has_payment_verified": self.has_payment_verified,
            "payment_date": self.payment_date.isoformat() if self.payment_date else None,
            "payment_transaction_id": self.payment_transaction_id,
            "payment_message": self.payment_message,
            "order_display_id": self.order_display_id,
        }

    @classmethod
    def from_entity(cls, order: Order) -> "OrderResponse":
        """Convert Order entity to OrderResponse DTO"""
        return cls(
            internal_id=order.internal_id,
            customer_internal_id=order.customer_internal_id,
            order_items=[OrderItemResponse.from_entity(item) for item in order.order_items],
            value=order.value.value if order.value else 0.0,
            status=str(order.status),
            start_date=order.start_date,
            end_date=order.end_date,
            has_payment_verified=order.has_payment_verified,
            payment_date=order.payment_date,
            payment_transaction_id=order.payment_transaction_id,
            payment_message=order.payment_message,
            order_display_id=order.order_display_id
        )


@dataclass
class OrderListResponse(ResponseInterface):
    """Response DTO for order list"""
    orders: List[OrderResponse]
    total: int
    skip: int
    limit: int

    def to_dict(self) -> dict:
        return {
            "orders": [order.to_dict() for order in self.orders],
            "total": self.total,
            "skip": self.skip,
            "limit": self.limit,
        }

    @classmethod
    def from_entity(cls, orders: List[Order], skip: int, limit: int) -> "OrderListResponse":
        """Convert list of Order entities to OrderListResponse DTO"""
        return cls(
            orders=[OrderResponse.from_entity(order) for order in orders],
            total=len(orders),
            skip=skip,
            limit=limit
        )


@dataclass
class PaymentStatusResponse(ResponseInterface):
    """Response DTO for payment status"""
    order_internal_id: int
    payment_date: Optional[str]
    payment_transaction_id: str
    payment_message: str
    has_payment_verified: bool
    value: float
    status: str

    def to_dict(self) -> dict:
        return {
            "order_internal_id": self.order_internal_id,
            "payment_date": self.payment_date,
            "payment_transaction_id": self.payment_transaction_id,
            "payment_message": self.payment_message,
            "has_payment_verified": self.has_payment_verified,
            "value": self.value,
            "status": self.status,
        }

    @classmethod
    def from_entity(cls, order: Order) -> "PaymentStatusResponse":
        """Convert Order entity to PaymentStatusResponse DTO"""
        return cls(
            order_internal_id=order.internal_id,
            payment_date=order.payment_date.isoformat() if order.payment_date else None,
            payment_transaction_id=order.payment_transaction_id,
            payment_message=order.payment_message,
            has_payment_verified=order.has_payment_verified,
            value=order.value.value if order.value else 0.0,
            status=str(order.status)
        ) 
