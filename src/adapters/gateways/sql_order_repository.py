from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING


from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from src.adapters.gateways.shared_base import Base
from src.adapters.gateways.interfaces.database_interface import DatabaseInterface
from src.application.repositories.order_repository import OrderRepository
from src.entities.order import Order, OrderItem
from src.entities.product import Product
from src.entities.ingredient import Ingredient

from src.entities.value_objects.money import Money
from src.entities.value_objects.order_status import OrderStatus, OrderStatusType

if TYPE_CHECKING:
    from src.application.repositories.product_repository import ProductRepository
    from src.application.repositories.ingredient_repository import IngredientRepository

# Import the related models for relationships (will be available after all models are loaded)
# These imports will work because of the shared Base


class OrderItemModel(Base):
    """SQLAlchemy model for order items"""
    __tablename__ = "order_items"

    internal_id = Column(Integer, primary_key=True, autoincrement=True)
    order_internal_id = Column(Integer, ForeignKey("orders.internal_id"), nullable=False)
    product_internal_id = Column(Integer, ForeignKey("products.internal_id"), nullable=False)
    additional_ingredient_internal_ids = Column(JSONB, nullable=True)  # JSON array of internal_ids
    remove_ingredient_internal_ids = Column(JSONB, nullable=True)  # JSON array of internal_ids
    item_receipt = Column(JSONB, nullable=True)  # JSON object
    price = Column(Float, nullable=False, default=0.0)

    # Relationships
    order = relationship("OrderModel", back_populates="order_items")
    product = relationship("ProductModel")


class OrderModel(Base):
    """SQLAlchemy model for orders"""
    __tablename__ = "orders"

    internal_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_internal_id = Column(Integer, ForeignKey("customers.internal_id"), nullable=False)
    value = Column(Float, nullable=False, default=0.0)
    status = Column(String(20), nullable=False, default="RECEBIDO")
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    has_payment_verified = Column(Boolean, nullable=False, default=False)
    payment_date = Column(DateTime, nullable=True)
    payment_transaction_id = Column(String(255), nullable=True)
    payment_message = Column(Text, nullable=True)
    order_display_id = Column(String(10), nullable=True)

    # Relationships
    customer = relationship("CustomerModel")
    order_items = relationship("OrderItemModel", back_populates="order", cascade="all, delete-orphan")


class SQLOrderRepository(OrderRepository):
    """SQLAlchemy implementation of OrderRepository"""

    def __init__(
        self,
        database: DatabaseInterface,
        product_repository: ProductRepository | None = None,
        ingredient_repository: IngredientRepository | None = None,
    ):
        self.database = database
        self.product_repository = product_repository
        self.ingredient_repository = ingredient_repository

    def create(self, order: Order) -> Order:
        """Create a new order"""
        try:
            with self.database.get_session() as session:
                # Use customer_internal_id directly
                customer_internal_id = order.customer_internal_id
                if not customer_internal_id:
                    raise ValueError("Order must have a customer_internal_id")

                # Create order model
                order_model = OrderModel(
                    customer_internal_id=customer_internal_id,
                    value=order.value.value if order.value else 0.0,
                    status=order.status.value,
                    start_date=order.start_date,
                    end_date=order.end_date,
                    has_payment_verified=order.has_payment_verified,
                    payment_date=order.payment_date,
                    payment_transaction_id=order.payment_transaction_id,
                    payment_message=order.payment_message,
                    order_display_id=order.order_display_id
                )

                session.add(order_model)
                session.commit()
                session.refresh(order_model)

                # Update order_display_id after getting internal_id from database
                if order_model.internal_id and not order_model.order_display_id:
                    order_model.order_display_id = str(order_model.internal_id).zfill(3)[:3]
                    session.commit()
                    session.refresh(order_model)

                # Create order item models after order is saved
                for item in order.order_items:
                    if not item.product:
                        raise ValueError(f"Order item {item.internal_id} must have a product")
                    
                    # Use product internal_id directly
                    if not item.product.internal_id:
                        raise ValueError("Product must have an internal_id")
                    
                    item_model = OrderItemModel(
                        order_internal_id=order_model.internal_id,
                        product_internal_id=item.product.internal_id,
                        additional_ingredient_internal_ids=self._serialize_ingredient_internal_ids(item.additional_ingredient, session),
                        remove_ingredient_internal_ids=self._serialize_ingredient_internal_ids(item.remove_ingredient, session),
                        item_receipt=self._serialize_item_receipt(item.get_item_receipt(), session),
                        price=item.price.value
                    )
                    session.add(item_model)

                session.commit()
                session.refresh(order_model)

                return self._to_entity(order_model)
        except Exception as e:
            raise ValueError(f"Failed to create order: {str(e)}")

    def get_by_id(self, order_internal_id: int) -> Optional[Order]:
        """Get order by ID"""
        with self.database.get_session() as session:
            order_model = session.query(OrderModel).filter(OrderModel.internal_id == order_internal_id).first()
            if not order_model:
                return None

            return self._to_entity(order_model)



    def get_by_status(self, status: str) -> List[Order]:
        """Get all orders with a specific status"""
        with self.database.get_session() as session:
            order_models = session.query(OrderModel).filter(OrderModel.status == status).all()
            return [self._to_entity(order_model) for order_model in order_models]

    def list_all(self, skip: int = 0, limit: int = 100) -> List[Order]:
        """List all orders with pagination"""
        with self.database.get_session() as session:
            order_models = session.query(OrderModel).offset(skip).limit(limit).all()
            return [self._to_entity(order_model) for order_model in order_models]

    def update(self, order: Order) -> Order:
        """Update an existing order"""
        with self.database.get_session() as session:
            order_model = session.query(OrderModel).filter(OrderModel.internal_id == order.internal_id).first()
            if not order_model:
                raise ValueError(f"Order with internal_id {order.internal_id} not found")

            # Update customer_internal_id if customer changed
            if order.customer_internal_id:
                order_model.customer_internal_id = order.customer_internal_id

            # Update order fields
            order_model.value = order.value.value if order.value else 0.0
            order_model.status = order.status.value
            order_model.start_date = order.start_date
            order_model.end_date = order.end_date
            order_model.has_payment_verified = order.has_payment_verified
            order_model.payment_date = order.payment_date
            order_model.payment_transaction_id = order.payment_transaction_id
            order_model.payment_message = order.payment_message
            order_model.order_display_id = order.order_display_id

            # Update order items (simplified - in real implementation you'd need more complex logic)
            # For now, we'll just update the existing items
            for item in order.order_items:
                item_model = session.query(OrderItemModel).filter(OrderItemModel.internal_id == item.internal_id).first()
                if item_model:                    
                    item_model.additional_ingredient_internal_ids = self._serialize_ingredient_internal_ids(item.additional_ingredient, session)
                    item_model.remove_ingredient_internal_ids = self._serialize_ingredient_internal_ids(item.remove_ingredient, session)
                    item_model.item_receipt = self._serialize_item_receipt(item.get_item_receipt(), session)
                    item_model.price = item.price.value

            # Update order_display_id if internal_id exists but display_id is empty
            if order_model.internal_id and not order_model.order_display_id:
                order_model.order_display_id = str(order_model.internal_id).zfill(3)[:3]

            session.commit()
            session.refresh(order_model)

            return self._to_entity(order_model)

    def cancel(self, order_internal_id: int) -> bool:
        """Cancel an order by ID"""
        with self.database.get_session() as session:
            order_model = session.query(OrderModel).filter(OrderModel.internal_id == order_internal_id).first()
            if not order_model:
                return False

            # Update status to cancelled
            order_model.status = OrderStatusType.CANCELADO.value
            session.commit()
            return True

    def update_status(self, order_internal_id: int, status: str) -> Optional[Order]:
        """Update order status"""
        with self.database.get_session() as session:
            order_model = session.query(OrderModel).filter(OrderModel.internal_id == order_internal_id).first()
            if not order_model:
                return None

            order_model.status = status
            session.commit()
            session.refresh(order_model)

            return self._to_entity(order_model)

    def process_payment(self, order_internal_id: int, payment_data: dict) -> Optional[Order]:
        """Process payment for an order"""
        with self.database.get_session() as session:
            order_model = session.query(OrderModel).filter(OrderModel.internal_id == order_internal_id).first()
            if not order_model:
                return None

            order_model.payment_transaction_id = payment_data.get('transaction_id', '')
            order_model.payment_date = payment_data.get('date')
            order_model.payment_message = payment_data.get('message', '')

            if payment_data.get('approval_status', False):
                order_model.has_payment_verified = True
                order_model.status = OrderStatusType.EM_PREPARACAO.value
            else:
                order_model.has_payment_verified = False
                order_model.status = OrderStatusType.CANCELADO.value

            session.commit()
            session.refresh(order_model)

            return self._to_entity(order_model)

    def get_payment_status(self, order_internal_id: int) -> Optional[dict]:
        """Get payment status for an order"""
        with self.database.get_session() as session:
            order_model = session.query(OrderModel).filter(OrderModel.internal_id == order_internal_id).first()
            if not order_model:
                return None

            return {
                "payment_date": order_model.payment_date.isoformat() if order_model.payment_date else None,
                "payment_transaction_id": order_model.payment_transaction_id,
                "payment_message": order_model.payment_message,
                "has_payment_verified": order_model.has_payment_verified,
                "value": order_model.value,
                "status": order_model.status
            }

    def _to_entity(self, order_model: OrderModel) -> Order:
        """Convert OrderModel to Order entity with minimal external lookups"""
        product_cache = self._load_products(order_model)
        ingredient_cache = self._load_ingredients(order_model)

        order_items = []
        for item_model in order_model.order_items:
            product = None
            product_id = getattr(item_model, "product_internal_id", None)
            if self.product_repository and product_id:
                product = product_cache.get(product_id)
            if not product:
                raise ValueError(
                    "Product repository is required to hydrate order items; provide it to SQLOrderRepository."
                )

            item_receipt = []
            if item_model.item_receipt:
                try:
                    item_receipt = self._deserialize_item_receipt(
                        item_model.item_receipt,
                        self.ingredient_repository
                    )
                except Exception as e:
                    print(f"Warning: Could not deserialize item receipt: {e}")

            additional_ingredients = []
            if self.ingredient_repository and item_model.additional_ingredient_internal_ids:
                try:
                    internal_ids = self._deserialize_ingredient_internal_ids(
                        item_model.additional_ingredient_internal_ids
                    )
                    for internal_id in internal_ids:
                        ingredient = ingredient_cache.get(internal_id)
                        if ingredient:
                            additional_ingredients.append(ingredient)
                except Exception as e:
                    print(f"Warning: Could not load additional ingredients: {e}")

            remove_ingredients = []
            if self.ingredient_repository and item_model.remove_ingredient_internal_ids:
                try:
                    internal_ids = self._deserialize_ingredient_internal_ids(
                        item_model.remove_ingredient_internal_ids
                    )
                    for internal_id in internal_ids:
                        ingredient = ingredient_cache.get(internal_id)
                        if ingredient:
                            remove_ingredients.append(ingredient)
                except Exception as e:
                    print(f"Warning: Could not load remove ingredients: {e}")

            order_item = OrderItem(
                order_internal_id=order_model.internal_id,
                product=product,
                additional_ingredient=additional_ingredients,
                remove_ingredient=remove_ingredients,
                item_receipt=item_receipt,
                price=Money(amount=item_model.price),
                internal_id=item_model.internal_id
            )

            order_items.append(order_item)

        return Order(
            customer_internal_id=order_model.customer_internal_id,
            order_items=order_items,
            value=Money(amount=order_model.value),
            status=OrderStatus.create(order_model.status),
            start_date=order_model.start_date,
            end_date=order_model.end_date,
            has_payment_verified=order_model.has_payment_verified,
            payment_date=order_model.payment_date,
            payment_transaction_id=order_model.payment_transaction_id,
            payment_message=order_model.payment_message,
            internal_id=order_model.internal_id,
            order_display_id=order_model.order_display_id,
            _skip_active_validation=True
        )

    def _load_products(self, order_model: OrderModel) -> dict[int, Product]:
        """Load all products for an order once to avoid repeated catalog calls"""
        if not self.product_repository:
            return {}

        product_ids = {
            getattr(item_model, "product_internal_id", None)
            for item_model in order_model.order_items
            if getattr(item_model, "product_internal_id", None)
        }

        cache: dict[int, Product] = {}
        for product_id in product_ids:
            try:
                cache[product_id] = self.product_repository.find_by_id(
                    product_id, include_inactive=True
                )
            except Exception as exc:
                print(f"Warning: Could not load product {product_id}: {exc}")
        return cache

    def _load_ingredients(self, order_model: OrderModel):
        """Load all ingredients for an order once to avoid repeated catalog calls"""
        if not self.ingredient_repository:
            return {}

        ingredient_ids: set[int] = set()
        for item_model in order_model.order_items:
            ingredient_ids.update(
                self._deserialize_ingredient_internal_ids(
                    item_model.additional_ingredient_internal_ids
                ) or []
            )
            ingredient_ids.update(
                self._deserialize_ingredient_internal_ids(
                    item_model.remove_ingredient_internal_ids
                ) or []
            )
            for receipt_item in item_model.item_receipt or []:
                internal_id = receipt_item.get("ingredient_internal_id")
                if internal_id:
                    ingredient_ids.add(internal_id)

        cache: dict[int, Ingredient] = {}
        for ingredient_id in ingredient_ids:
            try:
                ingredient = self.ingredient_repository.find_by_id(
                    ingredient_id, include_inactive=True
                )
                if ingredient:
                    cache[ingredient_id] = ingredient
            except Exception as exc:
                print(f"Warning: Could not load ingredient {ingredient_id}: {exc}")
        return cache

    def _serialize_ingredient_ids(self, ingredients: List) -> str:
        """Serialize ingredient IDs to JSON string"""
        import json
        return json.dumps([str(ing.internal_id) for ing in ingredients])

    def _deserialize_ingredient_ids(self, ingredient_ids_json: str) -> List[str]:
        """Deserialize ingredient IDs from JSON string"""
        import json
        try:
            return json.loads(ingredient_ids_json)
        except (json.JSONDecodeError, TypeError):
            return []

    def _serialize_ingredient_internal_ids(self, ingredients: List, session) -> List[int]:
        """Serialize ingredient internal_ids to list for JSONB storage"""
        internal_ids = []
        for ingredient in ingredients:
            if ingredient.internal_id:
                internal_ids.append(ingredient.internal_id)
        
        return internal_ids

    def _deserialize_ingredient_internal_ids(self, ingredient_internal_ids: List[int]) -> List[int]:
        """Get ingredient internal_ids from JSONB data"""
        try:
            return ingredient_internal_ids if ingredient_internal_ids else []
        except (TypeError, AttributeError):
            return []

    def _serialize_item_receipt(self, item_receipt: List, session=None) -> List[dict]:
        """Serialize item receipt to list of dicts for JSONB storage using ingredient internal_ids"""
        receipt_data = []
        for item in item_receipt:
            if item.ingredient.internal_id:
                receipt_data.append({
                    "ingredient_internal_id": item.ingredient.internal_id,
                    "quantity": item.quantity
                })
        
        return receipt_data

    def _deserialize_item_receipt(self, item_receipt_data: List[dict], ingredient_repository: IngredientRepository) -> List:
        """Deserialize item receipt from JSONB data using ingredient internal_ids"""
        from src.entities.product import ProductReceiptItem
        
        try:
            receipt_items = []
            
            for item_data in item_receipt_data or []:
                # Use new format with ingredient_internal_id
                ingredient_internal_id = item_data.get("ingredient_internal_id")
                quantity = item_data.get("quantity", 1)
                
                ingredient = None
                if ingredient_repository and ingredient_internal_id:
                    # Use internal_id to find ingredient - include inactive ingredients for historical data
                    ingredient = ingredient_repository.find_by_id(ingredient_internal_id, include_inactive=True)
                
                if ingredient:
                    receipt_items.append(ProductReceiptItem(
                        ingredient=ingredient,
                        quantity=quantity
                    ))
            
            return receipt_items
        except (TypeError, AttributeError):
            return [] 
