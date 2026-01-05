from datetime import datetime
from typing import Any
from http import HTTPStatus

from src.adapters.presenters.interfaces.presenter_interface import PresenterInterface
from src.application.dto.interfaces.response_interface import ResponseInterface
from src.application.exceptions import (
    CustomerValidationException,
    CustomerNotFoundException,
    CustomerAlreadyExistsException,
    CustomerBusinessRuleException,
    IngredientValidationException,
    IngredientNotFoundException,
    IngredientAlreadyExistsException,
    IngredientBusinessRuleException,
    ProductValidationException,
    ProductNotFoundException,
    ProductAlreadyExistsException,
    ProductBusinessRuleException,
    AuthenticationException,
    AuthorizationException,
)



class JSONPresenter(PresenterInterface):
    """
    JSON presenter for REST API responses.

    In Clean Architecture:
    - This is part of the Interface Adapters layer
    - It formats data for JSON responses
    - It handles error formatting
    - It provides consistent API response structure
    """

    def present(self, data: Any) -> dict:
        """Present single data item as JSON"""
        return self._present_generic(data)

    def present_list(self, data_list: list) -> dict:
        """Present list of data as JSON"""
        if not data_list:
            return {"data": [], "total_count": 0, "timestamp": self._get_timestamp()}

        # Handle different types of lists
        return {
                "data": [self._present_generic(item) for item in data_list],
                "total_count": len(data_list),
                "timestamp": self._get_timestamp(),
            }

    def present_error(self, error: Exception) -> dict:
        """Present error as JSON"""
        error_response = {
            "error": {
                "message": str(error),
                "type": type(error).__name__,
                "timestamp": self._get_timestamp(),
            }
        }

        # Add HTTP status code if available
        if hasattr(error, "status_code"):
            error_response["error"]["status_code"] = error.status_code
        else:
            # Map specific exceptions to appropriate HTTP status codes
            error_response["error"]["status_code"] = self._get_status_code_for_exception(error)

        return error_response

    def _get_status_code_for_exception(self, error: Exception) -> int:
        """Get appropriate HTTP status code for different exception types"""
        
        # Validation exceptions - 400 Bad Request
        if isinstance(error, (
            CustomerValidationException,
            IngredientValidationException,
            ProductValidationException,
            ValueError,
        )):
            return HTTPStatus.BAD_REQUEST
        
        # Not found exceptions - 404 Not Found
        elif isinstance(error, (
            CustomerNotFoundException,
            IngredientNotFoundException,
            ProductNotFoundException,
            FileNotFoundError,
        )):
            return HTTPStatus.NOT_FOUND
        
        # Conflict exceptions - 409 Conflict
        elif isinstance(error, (
            CustomerAlreadyExistsException,
            IngredientAlreadyExistsException,
            ProductAlreadyExistsException,
        )):
            return HTTPStatus.CONFLICT
        
        # Business rule violations - 400 Bad Request
        elif isinstance(error, (
            CustomerBusinessRuleException,
            IngredientBusinessRuleException,
            ProductBusinessRuleException,
        )):
            return HTTPStatus.BAD_REQUEST
        
        # Authentication exceptions - 401 Unauthorized
        elif isinstance(error, AuthenticationException):
            return HTTPStatus.UNAUTHORIZED
        
        # Authorization exceptions - 403 Forbidden
        elif isinstance(error, AuthorizationException):
            return HTTPStatus.FORBIDDEN
        
        # Default to 500 Internal Server Error for unknown exceptions
        else:
            return HTTPStatus.INTERNAL_SERVER_ERROR

    def _present_generic(self, data: Any) -> dict:
        """Present generic data in JSON format"""
        if hasattr(data, "to_dict"):
            result = data.to_dict()
            # Add timestamp to ResponseInterface DTOs
            if isinstance(data, ResponseInterface):
                result["timestamp"] = self._get_timestamp()
            return result
        elif hasattr(data, "__dict__"):
            return data.__dict__
        else:
            return {"data": str(data), "timestamp": self._get_timestamp()}

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        return datetime.utcnow().isoformat() + "Z"


