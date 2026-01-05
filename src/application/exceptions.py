"""
Custom exceptions for the application layer.

In Clean Architecture:
- These exceptions are part of the Application Business Rules layer
- They provide specific error types for different business scenarios
- They help standardize error handling across use cases
"""


class ApplicationException(Exception):
    """Base exception for application layer errors"""

    pass


class CustomerNotFoundException(ApplicationException):
    """Raised when a customer is not found"""

    pass


class CustomerAlreadyExistsException(ApplicationException):
    """Raised when trying to create a customer that already exists"""

    pass


class CustomerValidationException(ApplicationException):
    """Raised when customer data validation fails"""

    pass


class CustomerBusinessRuleException(ApplicationException):
    """Raised when a business rule is violated"""

    pass


class CustomerOperationException(ApplicationException):
    """Raised when a customer operation fails"""

    pass


class AuthenticationException(ApplicationException):
    """Raised when authentication fails"""

    pass


class AuthorizationException(ApplicationException):
    """Raised when authorization fails"""

    pass


class DatabaseException(ApplicationException):
    """Raised when database operations fail"""

    pass

class IngredientNotFoundException(ApplicationException):
    """Raised when a ingredient is not found"""

    pass


class IngredientAlreadyExistsException(ApplicationException):
    """Raised when a ingredient already exists"""

    pass

class IngredientValidationException(ApplicationException):
    """Raised when a ingredient validation fails"""

    pass

class IngredientBusinessRuleException(ApplicationException):
    """Raised when a ingredient business rule is violated"""

    pass

class ProductNotFoundException(ApplicationException):
    """Raised when a product is not found"""

    pass

class ProductAlreadyExistsException(ApplicationException):
    """Raised when a product already exists"""

    pass

class ProductValidationException(ApplicationException):
    """Raised when a product validation fails"""

    pass

class ProductBusinessRuleException(ApplicationException):
    """Raised when a product business rule is violated"""

    pass


class OrderNotFoundException(ApplicationException):
    """Raised when an order is not found"""

    pass


class OrderAlreadyExistsException(ApplicationException):
    """Raised when an order already exists"""

    pass


class OrderValidationException(ApplicationException):
    """Raised when an order validation fails"""

    pass


class OrderBusinessRuleException(ApplicationException):
    """Raised when an order business rule is violated"""

    pass


class PaymentException(ApplicationException):
    """Raised when payment operations fail"""

    pass


class PaymentNotFoundException(ApplicationException):
    """Raised when a payment is not found"""

    pass
