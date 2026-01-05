from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

from src.entities.value_objects.money import Money
from src.entities.value_objects.order_status import OrderStatus
from src.entities.product import Product, ProductReceiptItem
from src.entities.ingredient import Ingredient


@dataclass
class OrderItem:
    """
    OrderItem entity that represents an item in an order.

    This is an entity because:
    - It has an identity (id)
    - It can change over time while maintaining its identity
    - It contains business logic and rules
    """

    order_internal_id: int
    product: Product
    additional_ingredient: List[Ingredient]
    remove_ingredient: List[Ingredient]
    item_receipt: List[ProductReceiptItem] = field(default_factory=list)
    price: Money = field(default_factory=lambda: Money(amount=0.0))
    internal_id: Optional[int] = None

    def __post_init__(self):
        """Validate business rules and initialize computed values"""
        self._generate_item_receipt()
        self._calculate_price()

    def _serialize_default_ingredients(self) -> List[Ingredient]:
        """Serialize default ingredients with quantities"""
        result = []
        for item in self.product.default_ingredient:
            if item.quantity > 1:
                result.extend([item.ingredient] * item.quantity)
            else:
                result.append(item.ingredient)
        return result

    def _generate_item_receipt(self):
        """Generate the final item receipt with all ingredients"""
        if self.item_receipt:
            return

        default_ingredient = self._serialize_default_ingredients()
        additional_ingredient = self.additional_ingredient
        remove_ingredient = self.remove_ingredient

        # Only keep default ingredients not in remove_ingredient
        filtered_default = [
            item for item in default_ingredient if item not in remove_ingredient
        ]

        # Combine all ingredients (filtered default + additional)
        full_list = filtered_default + additional_ingredient

        # Use internal_id for grouping to avoid duplicate objects with same internal_id
        ingredient_map = {}
        for ingredient in full_list:
            key = getattr(ingredient, "internal_id", id(ingredient))
            if key in ingredient_map:
                ingredient_map[key]["quantity"] += 1
            else:
                ingredient_map[key] = {"ingredient": ingredient, "quantity": 1}

        self.item_receipt = [
            ProductReceiptItem(
                ingredient=entry["ingredient"], quantity=entry["quantity"]
            )
            for entry in ingredient_map.values()
        ]

    def get_item_receipt(self) -> List[ProductReceiptItem]:
        """Get the item receipt, generating it if needed"""
        if not self.item_receipt:
            self._generate_item_receipt()
        return self.item_receipt

    def _calculate_price(self):
        """Calculate the total price for this item"""
        if self.price.amount != Money(amount=0.0).amount:
            return

        total_price = self.product.price
        for ingredient in self.additional_ingredient:
            total_price += ingredient.price
        self.price = total_price

    def __str__(self) -> str:
        return f"OrderItem(internal_id={self.internal_id}, product={self.product.name}, price={self.price})"

    def __repr__(self) -> str:
        return f"OrderItem(internal_id={self.internal_id}, product={self.product.name}, price={self.price})"


@dataclass
class Order:
    """
    Order entity that represents an order in the ordering system.

    This is an entity because:
    - It has an identity (id)
    - It can change over time while maintaining its identity
    - It contains business logic and rules
    - It's the aggregate root for order-related operations
    """

    customer_internal_id: int
    order_items: List[OrderItem]
    value: Optional[Money] = None
    status: Optional[OrderStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    has_payment_verified: bool = False
    payment_date: Optional[datetime] = None
    payment_transaction_id: str = ""
    payment_message: str = ""
    internal_id: Optional[int] = None
    order_display_id: str = ""
    _skip_active_validation: bool = False

    def __post_init__(self):
        """Validate business rules and initialize computed values"""
        if not self._skip_active_validation:
            self._validate_business_rules()
        else:
            self._validate_business_rules_skip_active_check()
        self._check_or_create_status()
        if self.value is not None:
            self.value = self.value
        else:
            self.calculate_value()
        self._set_display_id()

    def _validate_business_rules(self):
        """Validate domain business rules"""
        if not self.customer_internal_id:
            raise ValueError("Order must have a customer internal ID")
        
        if not self.order_items:
            raise ValueError("Order must have at least one item")
        
        # Business rule: All order items must have valid products
        for item in self.order_items:
            if not item.product or not item.product.is_active:
                raise ValueError("Order items must have active products")
        
        # Business rule: Order value must be positive
        if self.value and self.value.amount <= 0:
            raise ValueError("Order value must be positive")

    def _set_display_id(self):
        """Set the display ID based on internal ID"""
        if self.internal_id:
            self.order_display_id = str(self.internal_id).zfill(3)[:3]
        return self.order_display_id
    
    def update_display_id(self):
        """Update the display ID after internal_id is set (usually after database save)"""
        if self.internal_id and not self.order_display_id:
            self.order_display_id = str(self.internal_id).zfill(3)[:3]
        return self.order_display_id

    def _check_or_create_status(self):
        """Create default status if not provided"""
        if not self.status:
            self.status = OrderStatus.recebido()

    def set_start_date(self):
        """Set the order start date to current time"""
        self.start_date = datetime.now()

    def set_end_date(self):
        """Set the order end date to current time"""
        self.end_date = datetime.now()

    def validate_duplicated_payment(self):
        """Validate that payment hasn't been processed before"""
        if self.has_payment_verified:
            raise ValueError("Payment has already been verified for this order")

    def next_status(self):
        """Move to the next status in the flow"""
        next_status = self.status.next_status()
        if next_status:
            self.status = next_status

    def calculate_value(self):
        """Calculate the total order value"""
        total_value = Money(amount=0.0)

        for item in self.order_items:
            total_value += (
                Money(amount=item.price.amount)
                if not isinstance(item.price, Money)
                else item.price
            )

        self.value = total_value

    def process_payment(self, payment: dict):
        """Process payment and update order status accordingly"""
        self.payment_transaction_id = payment.get('transaction_id', '')
        self.payment_date = payment.get('date')
        self.payment_message = payment.get('message', '')

        if payment.get('approval_status', False):
            self.validate_duplicated_payment()
            self.has_payment_verified = True
            self.status = OrderStatus.em_preparacao()
        else:
            self.has_payment_verified = False
            self.status = OrderStatus.cancelado()

    def can_be_cancelled(self) -> bool:
        """Check if the order can be cancelled"""
        return self.status and str(self.status) in ["RECEBIDO", "EM_PREPARACAO"]

    def can_be_finalized(self) -> bool:
        """Check if the order can be finalized"""
        return self.status and str(self.status) == "PRONTO"

    def get_total_items(self) -> int:
        """Get the total number of items in the order"""
        return len(self.order_items)

    @property
    def payment_as_dict(self) -> dict:
        """Get payment information as dictionary"""
        return {
            "payment_date": self.payment_date.isoformat() if self.payment_date else None,
            "payment_transaction_id": self.payment_transaction_id,
            "payment_message": self.payment_message,
            "has_payment_verified": self.has_payment_verified,
            "value": self.value.amount if hasattr(self.value, 'amount') else self.value,
            "status": str(self.status)
        }

    def __str__(self) -> str:
        return f"Order(internal_id={self.internal_id}, customer_id={self.customer_internal_id}, status={self.status}, value={self.value})"

    def __repr__(self) -> str:
        return f"Order(internal_id={self.internal_id}, customer_id={self.customer_internal_id}, status={self.status}, value={self.value})"

    @classmethod
    def create(
        cls,
        customer_internal_id: int,
        order_items: List[OrderItem],
        internal_id: Optional[int] = None,
        **kwargs
    ) -> "Order":
        """Factory method to create an Order"""
        return cls(
            customer_internal_id=customer_internal_id,
            order_items=order_items,
            internal_id=internal_id,
            **kwargs
        )

    def _validate_business_rules_skip_active_check(self):
        """Validate business rules without checking active products (for historical data)"""
        if not self.customer_internal_id:
            raise ValueError("Order must have a customer internal ID")
        
        if not self.order_items:
            raise ValueError("Order must have at least one item")
        
        # Business rule: Order value must be positive
        if self.value and self.value.amount <= 0:
            raise ValueError("Order value must be positive")

    @classmethod
    def create_with_items(
        cls,
        customer_internal_id: int,
        products: List[Product],
        additional_ingredients: List[List[Ingredient]] = None,
        remove_ingredients: List[List[Ingredient]] = None,
        order_internal_id: Optional[int] = None,
        internal_id: Optional[int] = None,
        **kwargs
    ) -> "Order":
        """Factory method to create an Order with products and ingredients"""
        if additional_ingredients is None:
            additional_ingredients = [[] for _ in products]
        if remove_ingredients is None:
            remove_ingredients = [[] for _ in products]

        order_items = []
        for i, product in enumerate(products):
            item = OrderItem(
                order_internal_id=order_internal_id or 0,  # Will be set when order is saved
                product=product,
                additional_ingredient=additional_ingredients[i],
                remove_ingredient=remove_ingredients[i]
            )
            order_items.append(item)

        return cls.create(
            customer_internal_id=customer_internal_id,
            order_items=order_items,
            internal_id=internal_id,
            **kwargs
        )

 