from datetime import datetime


from fastapi import HTTPException

from src.adapters.presenters.interfaces.presenter_interface import PresenterInterface
from src.application.repositories.order_repository import OrderRepository
from src.application.use_cases.order_use_cases import (
    OrderCreateUseCase,
    OrderReadUseCase,
    OrderUpdateUseCase,
    OrderListUseCase,
    OrderStatusUpdateUseCase,
    OrderPaymentProcessUseCase,
    OrderPaymentStatusUseCase,
    OrderPaymentRequestUseCase,
    OrderByStatusUseCase,
    OrderCancelUseCase,
)
from src.application.dto.implementation.order_dto import (
    OrderCreateRequest,
    OrderUpdateRequest,
    PaymentRequest,
    OrderItemRequest
)


class OrderController:
    """Controller for order-related HTTP endpoints"""

    def __init__(
        self,
        order_repository: OrderRepository,
        presenter: PresenterInterface
    ):
        self.order_repository = order_repository
        self.presenter = presenter

        # Initialize use cases
        self.create_use_case = OrderCreateUseCase(
            order_repository
        )
        self.read_use_case = OrderReadUseCase(order_repository)
        self.update_use_case = OrderUpdateUseCase(order_repository)
        self.cancel_use_case = OrderCancelUseCase(order_repository)
        self.list_use_case = OrderListUseCase(order_repository)
        self.status_update_use_case = OrderStatusUpdateUseCase(order_repository)
        self.payment_process_use_case = OrderPaymentProcessUseCase(order_repository)
        self.payment_status_use_case = OrderPaymentStatusUseCase(order_repository)
        # payment_request_use_case será injetado externamente, pois depende do client HTTP
        self.by_status_use_case = OrderByStatusUseCase(order_repository)
        self.payment_request_use_case: OrderPaymentRequestUseCase | None = None

    def create_order(self, data: dict, login: str) -> dict:
        """Create a new order"""
        try:
            # Convert data to DTO
            order_items = []
            for item_data in data.get("order_items", []):
                order_item = OrderItemRequest(
                    product_internal_id=item_data["product_internal_id"],
                    additional_ingredient_internal_ids=item_data.get("additional_ingredient_internal_ids", []),
                    remove_ingredient_internal_ids=item_data.get("remove_ingredient_internal_ids", [])
                )
                order_items.append(order_item)

            request = OrderCreateRequest(
                customer_internal_id=data["customer_internal_id"],
                order_items=order_items
            )

            result = self.create_use_case.execute(request)
            return self.presenter.present(result)

        except ValueError as e:
            error_response = self.presenter.present_error(e)
            raise HTTPException(status_code=400, detail=error_response)
        except Exception as e:
            error_response = self.presenter.present_error(e)
            raise HTTPException(status_code=500, detail=error_response)

    def get_order(self, order_internal_id: int, login: str) -> dict:
        """Get order by ID"""
        try:
            result = self.read_use_case.execute(order_internal_id)
            if not result:
                raise HTTPException(status_code=404, detail="Order not found")

            return self.presenter.present(result)

        except HTTPException:
            raise
        except Exception as e:
            error_response = self.presenter.present_error(e)
            raise HTTPException(status_code=500, detail=error_response)

    def update_order(self, order_internal_id: int, data: dict, login: str) -> dict:
        """Update an order"""
        try:
            request = OrderUpdateRequest(
                status=data.get("status"),
                order_items=data.get("order_items")
            )

            result = self.update_use_case.execute(order_internal_id, request)
            if not result:
                raise HTTPException(status_code=404, detail="Order not found")

            return self.presenter.present(result)

        except HTTPException:
            raise
        except ValueError as e:
            error_response = self.presenter.present_error(e)
            raise HTTPException(status_code=400, detail=error_response)
        except Exception as e:
            error_response = self.presenter.present_error(e)
            raise HTTPException(status_code=500, detail=error_response)

    def cancel_order(self, order_internal_id: int, login: str) -> dict:
        """Cancel an order"""
        try:
            success = self.cancel_use_case.execute(order_internal_id)
            if not success:
                raise HTTPException(status_code=404, detail="Order not found")

            return self.presenter.present({"message": "Order canceled successfully"})

        except HTTPException:
            raise
        except Exception as e:
            error_response = self.presenter.present_error(e)
            raise HTTPException(status_code=500, detail=error_response)

    def list_orders(self, skip: int = 0, limit: int = 100, login: str = None) -> dict:
        """List all orders"""
        try:
            result = self.list_use_case.execute(skip=skip, limit=limit)
            return self.presenter.present(result)

        except Exception as e:
            error_response = self.presenter.present_error(e)
            raise HTTPException(status_code=500, detail=error_response)

    def update_order_status(self, order_internal_id: int, status: str, login: str) -> dict:
        """Update order status"""
        try:
            # Convert OrderStatusType enum to string if needed
            status_str = status.value if hasattr(status, 'value') else str(status)
            result = self.status_update_use_case.execute(order_internal_id, status_str)
            if not result:
                raise HTTPException(status_code=404, detail="Order not found")

            return self.presenter.present(result)

        except HTTPException:
            raise
        except ValueError as e:
            error_response = self.presenter.present_error(e)
            raise HTTPException(status_code=400, detail=error_response)
        except Exception as e:
            error_response = self.presenter.present_error(e)
            raise HTTPException(status_code=500, detail=error_response)

    def process_payment(self, order_internal_id: int, data: dict, login: str) -> dict:
        """Process payment for an order"""
        try:
            print(f"Processing payment data: {data}")
            print(f"Date type: {type(data.get('date'))}, Value: {data.get('date')}")
            
            # Ensure date is a string before parsing
            date_str = str(data.get("date")) if data.get("date") else None
            payment_date = datetime.fromisoformat(date_str) if date_str else datetime.now()
            
            payment_request = PaymentRequest(
                transaction_id=data["transaction_id"],
                approval_status=data["approval_status"],
                date=payment_date,
                message=data.get("message", "")
            )

            result = self.payment_process_use_case.execute(order_internal_id, payment_request)
            if not result:
                raise HTTPException(status_code=404, detail="Order not found")

            return self.presenter.present(result)

        except HTTPException:
            raise
        except ValueError as e:
            error_response = self.presenter.present_error(e)
            raise HTTPException(status_code=400, detail=error_response)
        except Exception as e:
            error_response = self.presenter.present_error(e)
            raise HTTPException(status_code=500, detail=error_response)

    def get_payment_status(self, order_internal_id: int, login: str) -> dict:
        """Get payment status for an order"""
        try:
            result = self.payment_status_use_case.execute(order_internal_id)
            if not result:
                raise HTTPException(status_code=404, detail="Order not found")

            return self.presenter.present(result)

        except HTTPException:
            raise
        except Exception as e:
            error_response = self.presenter.present_error(e)
            raise HTTPException(status_code=500, detail=error_response)

    def request_payment(self, order_internal_id: int, login: str) -> dict:
        """Initiate payment via payment-service"""
        if not self.payment_request_use_case:
            raise HTTPException(status_code=503, detail="Payment client not configured")
        try:
            result = self.payment_request_use_case.execute(order_internal_id)
            return self.presenter.present(result)
        except HTTPException:
            raise
        except ValueError as e:
            error_response = self.presenter.present_error(e)
            raise HTTPException(status_code=400, detail=error_response)
        except Exception as e:
            error_response = self.presenter.present_error(e)
            raise HTTPException(status_code=500, detail=error_response)



    def get_orders_by_status(self, status: str, login: str) -> list:
        """Get orders by status"""
        try:
            result = self.by_status_use_case.execute(status)
            # Return the list directly since the route expects List[OrderResponseModel]
            return result

        except Exception as e:
            error_response = self.presenter.present_error(e)
            raise HTTPException(status_code=500, detail=error_response) 
