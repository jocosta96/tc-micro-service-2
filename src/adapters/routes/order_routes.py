from typing import List, Optional
from datetime import datetime


from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from src.adapters.controllers.order_controller import OrderController
from src.adapters.di.container import Container
from src.application.use_cases.order_use_cases import OrderPaymentRequestUseCase
from src.security.http_auth import check_credentials
from src.entities.value_objects.order_status import OrderStatusType


# Pydantic models for request/response
class OrderItemRequestModel(BaseModel):
    product_internal_id: int = Field(..., description="Product internal ID")
    additional_ingredient_internal_ids: Optional[List[int]] = Field(default=[], description="Additional ingredient internal IDs")
    remove_ingredient_internal_ids: Optional[List[int]] = Field(default=[], description="Remove ingredient internal IDs")


class OrderCreateRequestModel(BaseModel):
    customer_internal_id: int = Field(..., description="Customer internal ID")
    order_items: List[OrderItemRequestModel] = Field(..., description="Order items")


class OrderStatusUpdateRequestModel(BaseModel):
    status: OrderStatusType = Field(..., description="New order status")


class PaymentRequestModel(BaseModel):
    transaction_id: str = Field(..., description="Payment transaction ID")
    approval_status: bool = Field(..., description="Payment approval status")
    date: Optional[datetime] = Field(None, description="Payment date")
    message: Optional[str] = Field("", description="Payment message")


class PaymentRequestInitiateModel(BaseModel):
    # No amount field - payment amount will be taken from the order's value
    pass


class OrderItemResponseModel(BaseModel):
    internal_id: int
    product_internal_id: int
    product_name: str
    product_price: float
    additional_ingredients: List[int]  # These are ingredient internal IDs
    remove_ingredients: List[int]     # These are ingredient internal IDs
    item_receipt: List[dict]
    price: float


class OrderResponseModel(BaseModel):
    internal_id: int
    customer_internal_id: int
    order_items: List[OrderItemResponseModel]
    value: float
    status: str
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    has_payment_verified: bool
    payment_date: Optional[datetime]
    payment_transaction_id: str
    payment_message: str
    order_display_id: str


class OrderListResponseModel(BaseModel):
    orders: List[OrderResponseModel]
    total: int
    skip: int
    limit: int


class PaymentStatusResponseModel(BaseModel):
    order_internal_id: int
    payment_date: Optional[str]
    payment_transaction_id: str
    payment_message: str
    has_payment_verified: bool
    value: float
    status: str


class PaymentRequestResponseModel(BaseModel):
    order_id: int
    amount: float
    transaction_id: str
    payment_url: Optional[str]
    expires_at: Optional[str]


class MessageResponseModel(BaseModel):
    message: str


class SimpleResponseModel(BaseModel):
    data: str
    timestamp: str


class StatusIdResponseModel(BaseModel):
    status: str
    id: int


# Create router
order_router = APIRouter(tags=["order"], prefix="/order")


# Dependency injection function
def get_order_controller() -> OrderController:
    """Get order controller with dependencies"""
    container = Container()
    controller = OrderController(
        order_repository=container.order_repository,
        presenter=container.presenter
    )
    # injeta use case de request_payment com client HTTP externo
    controller.payment_request_use_case = OrderPaymentRequestUseCase(
        container.order_repository,
        container.payment_client
    )
    return controller


# Route definitions
@order_router.post("/create", response_model=OrderResponseModel, status_code=201)
async def create_order(
    order_data: OrderCreateRequestModel,
    controller: OrderController = Depends(get_order_controller),
    login: str = Depends(check_credentials)
):
    """Create a new order (checkout)"""
    return controller.create_order(order_data.dict(), login)


@order_router.get("/by-id/{order_id}", response_model=OrderResponseModel)
async def get_order(
    order_id: int,
    controller: OrderController = Depends(get_order_controller),
    login: str = Depends(check_credentials)
):
    """Get order by ID"""
    return controller.get_order(order_id, login)


@order_router.put("/update_status/{order_id}", response_model=OrderResponseModel)
async def update_order_status(
    order_id: int,
    order_data: OrderStatusUpdateRequestModel,
    controller: OrderController = Depends(get_order_controller),
    login: str = Depends(check_credentials)
):
    """Update order status"""
    return controller.update_order_status(order_id, order_data.status, login)


@order_router.delete("/cancel/{order_id}", response_model=SimpleResponseModel)
async def cancel_order(
    order_id: int,
    controller: OrderController = Depends(get_order_controller),
    login: str = Depends(check_credentials)
):
    """Cancel an order"""
    return controller.cancel_order(order_id, login)


@order_router.get("/list", response_model=OrderListResponseModel)
async def list_orders(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    controller: OrderController = Depends(get_order_controller),
    login: str = Depends(check_credentials)
):
    """List all orders with pagination"""
    return controller.list_orders(skip=skip, limit=limit, login=login)





@order_router.post("/payment_confirm/{order_id}", response_model=OrderResponseModel, include_in_schema=False)
async def process_payment(
    order_id: int,
    payment_data: PaymentRequestModel,
    controller: OrderController = Depends(get_order_controller),
    login: str = Depends(check_credentials)
):
    """Process payment for an order"""
    return controller.process_payment(order_id, payment_data.dict(), login)


@order_router.get("/payment_status/{order_id}", response_model=PaymentStatusResponseModel)
async def get_payment_status(
    order_id: int,
    controller: OrderController = Depends(get_order_controller),
    login: str = Depends(check_credentials)
):
    """Get payment status for an order"""
    return controller.get_payment_status(order_id, login)


@order_router.post("/request-payment/{order_id}", response_model=PaymentRequestResponseModel)
async def request_payment(
    order_id: int,
    controller: OrderController = Depends(get_order_controller),
    login: str = Depends(check_credentials)
):
    """Initiate payment via payment-service"""
    return controller.request_payment(order_id, login)




@order_router.get("/status/{status}", response_model=List[OrderResponseModel])
async def get_orders_by_status(
    status: OrderStatusType,
    controller: OrderController = Depends(get_order_controller),
    login: str = Depends(check_credentials)
):
    """Get orders by status"""
    return controller.get_orders_by_status(status.value, login) 
