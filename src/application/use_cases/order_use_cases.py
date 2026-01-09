import os
from typing import List, Optional


from src.application.repositories.order_repository import OrderRepository
from src.application.dto.implementation.order_dto import (
    OrderCreateRequest,
    OrderUpdateRequest,
    PaymentRequest,
    OrderResponse,
    OrderListResponse,
    PaymentStatusResponse,
    PaymentRequestResponse,
)
from src.entities.order import Order, OrderItem
from src.entities.product import Product
from src.entities.ingredient import Ingredient, IngredientType
from src.config.aws_ssm import get_ssm_client

from src.entities.value_objects.order_status import OrderStatus
from src.entities.value_objects.name import Name
from src.entities.value_objects.money import Money

from requests import get


class OrderCreateUseCase:
    """Use case for creating a new order"""

    def __init__(
        self,
        order_repository: OrderRepository,
    ):
        self.order_repository = order_repository

    def _fetch_catalog(self, path: str):
        """Fetch a resource from catalog service with basic validation"""

        host = get_ssm_client().get_parameter(
            "/ordering-system/catalog/apigateway/url",
            decrypt=True
        )  or \
        os.getenv("CATALOG_API_HOST")

        token = get_ssm_client().get_parameter(
            "/ordering-system/catalog/apigateway/token",
            decrypt=True
        )  or \
        os.getenv("CATALOG_API_TOKEN")


        if not host:
            raise ValueError("CATALOG_API_HOST is not configured")

        # Use HTTP for local development. Set CATALOG_API_HOST without protocol.
        url = f"{host}{path}"
        try:
            response = get(
                url, 
                timeout=5,
                headers={"Authorization": f"{token}"} if token else {}
            )
        except Exception as exc:
            raise ValueError(f"Failed to reach catalog service: {exc}") from exc

        if not response.ok:
            raise ValueError(
                f"Catalog service returned {response.status_code} for {url}"
            )

        return response.json()

    def _map_ingredient_fields(self, ingredient_data: dict) -> dict:
        """Map catalog ingredient fields to entity fields"""
        # Handle both naming conventions: appliesto_* and applies_to_*
        mapped = ingredient_data.copy()
        
        # Convert price to Money object if it's a number
        if "price" in mapped and not isinstance(mapped["price"], Money):
            if isinstance(mapped["price"], (int, float)):
                mapped["price"] = Money(amount=mapped["price"])
            elif isinstance(mapped["price"], dict) and "amount" in mapped["price"]:
                mapped["price"] = Money(**mapped["price"])
        
        # Map appliesto fields to applies_to if they exist
        if "appliesto_burger" in mapped:
            mapped["applies_to_burger"] = mapped.pop("appliesto_burger")
        if "appliesto_side" in mapped:
            mapped["applies_to_side"] = mapped.pop("appliesto_side")
        if "appliesto_drink" in mapped:
            mapped["applies_to_drink"] = mapped.pop("appliesto_drink")
        if "appliesto_dessert" in mapped:
            mapped["applies_to_dessert"] = mapped.pop("appliesto_dessert")
        
        # If applies_to fields are missing, infer from type
        if "applies_to_burger" not in mapped:
            ingredient_type = mapped.get("type", "")
            mapped["applies_to_burger"] = ingredient_type in ["bread", "meat", "cheese", "vegetable", "salad", "sauce"]
            mapped["applies_to_side"] = ingredient_type in ["salad", "sauce", "vegetable"]
            mapped["applies_to_drink"] = ingredient_type in ["ice", "milk"]
            mapped["applies_to_dessert"] = ingredient_type in ["topping"]
        
        return mapped

    def execute(self, request: OrderCreateRequest) -> OrderResponse:
        """Execute the order creation use case"""
        # Validate customer exists
        customer = self._fetch_catalog(
            f"/customer/by-id/{request.customer_internal_id}?include_inactive=false"
        )

        if not customer:
            raise ValueError(
                f"Customer with ID {request.customer_internal_id} not found"
            )

        # Business rule: Customer must be able to place orders
        if not customer["is_active"] or (
            not customer["is_anonymous"]
            and (not customer["email"] or not customer["document"])
        ):
            raise ValueError("Customer does not meet requirements to place orders")

        # Build order items
        order_items = []
        for item_request in request.order_items:
            # Get product - only allow active products for new orders
            product_request = self._fetch_catalog(
                f"/product/by-id/{item_request.product_internal_id}?include_inactive=false"
            )
            if not product_request:
                raise ValueError(
                    f"Product with ID {item_request.product_internal_id} not found or is deactivated"
                )

            # Additional validation: ensure product is active for new orders
            if not product_request["is_active"]:
                raise ValueError(
                    f"Product with ID {item_request.product_internal_id} is deactivated and cannot be added to new orders"
                )

            # Convert price to Money object if needed
            if "price" in product_request and not isinstance(product_request["price"], Money):
                if isinstance(product_request["price"], (int, float)):
                    product_request["price"] = Money(amount=product_request["price"])
                elif isinstance(product_request["price"], dict) and "amount" in product_request["price"]:
                    product_request["price"] = Money(**product_request["price"])

            # Convert default_ingredient from dict to ProductReceiptItem objects
            from src.entities.product import ProductReceiptItem
            default_ingredients = []
            for ing_data in product_request.get("default_ingredient", []):
                # Fetch complete ingredient data from catalog
                ingredient_response = self._fetch_catalog(
                    f"/ingredient/by-id/{ing_data.get('ingredient_internal_id')}?include_inactive=false"
                )
                if not ingredient_response:
                    raise ValueError(
                        f"Ingredient with ID {ing_data.get('ingredient_internal_id')} not found"
                    )
                
                ingredient_response = self._map_ingredient_fields(ingredient_response)
                ingredient_obj = Ingredient(**ingredient_response)
                default_ingredients.append(
                    ProductReceiptItem(
                        ingredient=ingredient_obj,
                        quantity=ing_data.get("quantity", 1)
                    )
                )
            
            product_request["default_ingredient"] = default_ingredients
            product = Product(**product_request)

            # Get additional ingredients - only allow active ingredients for new orders
            additional_ingredients = []
            for ing_id in item_request.additional_ingredient_internal_ids:
                ingredient = self._fetch_catalog(
                    f"/ingredient/by-id/{ing_id}?include_inactive=false"
                )
                if not ingredient:
                    raise ValueError(
                        f"Ingredient with ID {ing_id} not found or is deactivated"
                    )
                if not ingredient["is_active"]:
                    raise ValueError(
                        f"Ingredient with ID {ing_id} is deactivated and cannot be added to new orders"
                    )
                ingredient = self._map_ingredient_fields(ingredient)
                additional_ingredients.append(Ingredient(**ingredient))

            # Get remove ingredients - only allow active ingredients for new orders
            remove_ingredients = []
            for ing_id in item_request.remove_ingredient_internal_ids:
                ingredient = self._fetch_catalog(
                    f"/ingredient/by-id/{ing_id}?include_inactive=false"
                )
                if not ingredient:
                    raise ValueError(
                        f"Ingredient with ID {ing_id} not found or is deactivated"
                    )
                if not ingredient["is_active"]:
                    raise ValueError(
                        f"Ingredient with ID {ing_id} is deactivated and cannot be added to new orders"
                    )
                ingredient = self._map_ingredient_fields(ingredient)
                remove_ingredients.append(Ingredient(**ingredient))

            # Create order item
            order_item = OrderItem(
                order_internal_id=0,  # Will be set by Order entity
                product=product,
                additional_ingredient=additional_ingredients,
                remove_ingredient=remove_ingredients,
            )
            order_items.append(order_item)

        # Create order
        order = Order.create(
            customer_internal_id=request.customer_internal_id, order_items=order_items
        )

        # Set start date
        order.set_start_date()

        # Save order
        created_order = self.order_repository.create(order)

        return OrderResponse.from_entity(created_order)


class OrderReadUseCase:
    """Use case for reading order information"""

    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository

    def execute(self, order_internal_id: int) -> Optional[OrderResponse]:
        """Execute the order read use case"""
        order = self.order_repository.get_by_id(order_internal_id)
        if not order:
            return None

        return OrderResponse.from_entity(order)


class OrderListUseCase:
    """Use case for listing orders"""

    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository

    def execute(self, skip: int = 0, limit: int = 100) -> OrderListResponse:
        """Execute the order list use case"""
        orders = self.order_repository.list_all(skip=skip, limit=limit)
        return OrderListResponse.from_entity(orders, skip, limit)


class OrderUpdateUseCase:
    """Use case for updating an order"""

    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository

    def execute(
        self, order_internal_id: int, request: OrderUpdateRequest
    ) -> Optional[OrderResponse]:
        """Execute the order update use case"""
        order = self.order_repository.get_by_id(order_internal_id)
        if not order:
            return None

        # Update status if provided
        if request.status:
            order.status = OrderStatus.create(request.status)

        # Update order items if provided
        if request.order_items:
            # This would require more complex logic to rebuild order items
            # For now, we'll just update the status
            pass

        # Save updated order
        updated_order = self.order_repository.update(order)

        return OrderResponse.from_entity(updated_order)


class OrderStatusUpdateUseCase:
    """Use case for updating order status"""

    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository

    def execute(self, order_internal_id: int, status: str) -> Optional[OrderResponse]:
        """Execute the order status update use case"""
        order = self.order_repository.update_status(order_internal_id, status)
        if not order:
            return None

        return OrderResponse.from_entity(order)


class OrderPaymentProcessUseCase:
    """Use case for processing order payment"""

    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository

    def execute(
        self, order_internal_id: int, payment_request: PaymentRequest
    ) -> Optional[OrderResponse]:
        """Execute the order payment processing use case"""
        payment_data = {
            "transaction_id": payment_request.transaction_id,
            "approval_status": payment_request.approval_status,
            "date": payment_request.date,
            "message": payment_request.message,
        }

        order = self.order_repository.process_payment(order_internal_id, payment_data)
        if not order:
            return None

        return OrderResponse.from_entity(order)


class OrderPaymentStatusUseCase:
    """Use case for getting order payment status"""

    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository

    def execute(self, order_internal_id: int) -> Optional[PaymentStatusResponse]:
        """Execute the order payment status use case"""
        order = self.order_repository.get_by_id(order_internal_id)
        if not order:
            return None

        return PaymentStatusResponse.from_entity(order)


class OrderPaymentRequestUseCase:
    """Use case for requesting payment via payment-service"""

    def __init__(self, order_repository: OrderRepository, payment_client):
        self.order_repository = order_repository
        self.payment_client = payment_client

    def execute(self, order_internal_id: int) -> PaymentRequestResponse:
        order = self.order_repository.get_by_id(order_internal_id)
        if not order:
            raise ValueError(f"Order with ID {order_internal_id} not found")

        if order.has_payment_verified:
            raise ValueError("Order has already been paid")

        amount = order.value.value
        payment_data = self.payment_client.request_payment(order_internal_id, amount)

        return PaymentRequestResponse(
            order_id=order_internal_id,
            amount=amount,
            transaction_id=payment_data.get("transaction_id", ""),
            payment_url=payment_data.get("payment_url")
            or payment_data.get("qr_code")
            or payment_data.get("link"),
            expires_at=payment_data.get("expires_at"),
        )


class OrderCancelUseCase:
    """Use case for canceling an order"""

    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository

    def execute(self, order_internal_id: int) -> bool:
        """Execute the order cancel use case"""
        return self.order_repository.cancel(order_internal_id)


class OrderByStatusUseCase:
    """Use case for getting orders by status"""

    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository

    def execute(self, status: str) -> List[OrderResponse]:
        """Execute the order by status use case"""
        orders = self.order_repository.get_by_status(status)
        return [OrderResponse.from_entity(order) for order in orders]
