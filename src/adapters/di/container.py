
from src.application.repositories.order_repository import OrderRepository
from src.adapters.gateways.sql_order_repository import SQLOrderRepository
from src.adapters.gateways.http_product_repository import HTTPProductRepository
from src.adapters.gateways.http_ingredient_repository import HTTPIngredientRepository
from src.adapters.gateways.http_payment_client import HTTPPaymentClient
from src.adapters.gateways.implementations.sqlalchemy_database import SQLAlchemyDatabase
from src.adapters.gateways.interfaces.database_interface import DatabaseInterface
from src.adapters.presenters.implementations.json_presenter import JSONPresenter
from src.adapters.presenters.interfaces.presenter_interface import PresenterInterface


class Container:
    """
    Dependency Injection Container.

    In Clean Architecture:
    - This wires up all the components
    - It's part of the Frameworks & Drivers layer
    - It creates the concrete implementations
    - It manages the dependency graph
    """

    def __init__(self, database_url: str = None):
        self.database_url = database_url
        self._database: DatabaseInterface = None
        self._order_repository: OrderRepository = None
        self._product_repository = None
        self._ingredient_repository = None
        self._payment_client = None
        self._presenter: PresenterInterface = None

    @property
    def database(self) -> DatabaseInterface:
        """Get database instance"""
        if self._database is None:
            self._database = SQLAlchemyDatabase(self.database_url)
        return self._database

    @property
    def order_repository(self) -> OrderRepository:
        """Get order repository instance"""
        if self._order_repository is None:
            self._order_repository = SQLOrderRepository(
                self.database,
                product_repository=self.product_repository,
                ingredient_repository=self.ingredient_repository,
            )
        return self._order_repository

    @property
    def product_repository(self):
        """Get product repository client (catalog service)"""
        if self._product_repository is None:
            self._product_repository = HTTPProductRepository()
        return self._product_repository

    @property
    def ingredient_repository(self):
        """Get ingredient repository client (catalog service)"""
        if self._ingredient_repository is None:
            self._ingredient_repository = HTTPIngredientRepository()
        return self._ingredient_repository

    @property
    def payment_client(self):
        """Get payment service HTTP client"""
        if self._payment_client is None:
            self._payment_client = HTTPPaymentClient()
        return self._payment_client

    @property
    def presenter(self) -> PresenterInterface:
        """Get presenter instance"""
        if self._presenter is None:
            self._presenter = JSONPresenter()
        return self._presenter

    def reset(self):
        """Reset all dependencies (useful for testing)"""
        self._database = None
        self._order_repository = None
        self._product_repository = None
        self._ingredient_repository = None
        self._payment_client = None
        self._presenter = None


# Global container instance
container = Container()
