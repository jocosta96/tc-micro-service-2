from dataclasses import dataclass
from enum import Enum
from typing import Optional


class OrderStatusType(str, Enum):
    RECEBIDO = "RECEBIDO"
    EM_PREPARACAO = "EM_PREPARACAO"
    PRONTO = "PRONTO"
    FINALIZADO = "FINALIZADO"
    CANCELADO = "CANCELADO"


@dataclass(frozen=True)
class OrderStatus:
    """
    OrderStatus value object that represents a valid order status.

    This is a value object because:
    - It's immutable (frozen=True)
    - It validates itself during creation
    - It has no identity, only value
    - Two order status objects are equal if they have the same status
    """

    status: OrderStatusType

    def __post_init__(self):
        """Validate the order status during object creation"""
        if not self._is_valid_status(self.status):
            raise ValueError(f"Invalid order status: {self.status}")

    @staticmethod
    def _is_valid_status(status: OrderStatusType) -> bool:
        """Validates the order status"""
        return status in OrderStatusType

    def __str__(self) -> str:
        return str(self.status.value)

    def __repr__(self) -> str:
        return f"OrderStatus(status='{self.status.value}')"

    @classmethod
    def create(cls, status: str) -> "OrderStatus":
        """Factory method to create an OrderStatus value object"""
        try:
            status_enum = OrderStatusType(status)
            return cls(status=status_enum)
        except ValueError:
            raise ValueError(f"Invalid order status: {status}")

    @classmethod
    def recebido(cls) -> "OrderStatus":
        """Factory method to create a RECEBIDO status"""
        return cls(status=OrderStatusType.RECEBIDO)

    @classmethod
    def em_preparacao(cls) -> "OrderStatus":
        """Factory method to create an EM_PREPARACAO status"""
        return cls(status=OrderStatusType.EM_PREPARACAO)

    @classmethod
    def pronto(cls) -> "OrderStatus":
        """Factory method to create a PRONTO status"""
        return cls(status=OrderStatusType.PRONTO)

    @classmethod
    def finalizado(cls) -> "OrderStatus":
        """Factory method to create a FINALIZADO status"""
        return cls(status=OrderStatusType.FINALIZADO)

    @classmethod
    def cancelado(cls) -> "OrderStatus":
        """Factory method to create a CANCELADO status"""
        return cls(status=OrderStatusType.CANCELADO)

    def next_status(self) -> Optional["OrderStatus"]:
        """Get the next status in the flow"""
        flow = [
            OrderStatusType.RECEBIDO,
            OrderStatusType.EM_PREPARACAO,
            OrderStatusType.PRONTO,
            OrderStatusType.FINALIZADO
        ]
        try:
            current_index = flow.index(self.status)
            next_status = flow[current_index + 1]
            return OrderStatus(status=next_status)
        except (ValueError, IndexError):
            return None  # Already at FINALIZADO or invalid

    def previous_status(self) -> Optional["OrderStatus"]:
        """Get the previous status in the flow"""
        flow = [
            OrderStatusType.RECEBIDO,
            OrderStatusType.EM_PREPARACAO,
            OrderStatusType.PRONTO,
            OrderStatusType.FINALIZADO
        ]
        try:
            current_index = flow.index(self.status)
            prev_status = flow[current_index - 1]
            return OrderStatus(status=prev_status)
        except (ValueError, IndexError):
            return None  # Already at RECEBIDO or invalid

    @property
    def value(self) -> str:
        """Get the status value as string"""
        return self.status.value 