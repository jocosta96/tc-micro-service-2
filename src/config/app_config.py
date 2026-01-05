import os


class AppConfig:
    """
    Application configuration for the ordering system.

    In Clean Architecture:
    - This is part of the Frameworks & Drivers layer
    - It handles environment-specific configuration
    - It centralizes all configuration values
    """

    def __init__(self):
        # API Configuration
        self.api_prefix = os.getenv("API_PREFIX", "/fastfood/api")
        self.api_title = os.getenv("API_TITLE", "FastFood Ordering System")
        self.api_version = os.getenv("API_VERSION", "1.0.0")
        self.api_description = os.getenv(
            "API_DESCRIPTION", "A clean architecture ordering system"
        )

        # CORS Configuration
        self.allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
        self.allowed_credentials = (
            os.getenv("ALLOWED_CREDENTIALS", "true").lower() == "true"
        )
        self.allowed_methods = os.getenv(
            "ALLOWED_METHODS", "GET,POST,PUT,DELETE,OPTIONS"
        ).split(",")
        self.allowed_headers = os.getenv("ALLOWED_HEADERS", "*").split(",")

        # Logging Configuration
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_format = os.getenv(
            "LOG_FORMAT",
            "%(levelname)s:%(message)s:%(pathname)s:%(funcName)s:%(lineno)d",
        )

        # Rate Limiting Configuration
        self.rate_limit_enabled = (
            os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
        )
        self.rate_limit_default = os.getenv("RATE_LIMIT_DEFAULT", "100/minute")

        # Business Rules Configuration
        self.anonymous_email = os.getenv("ANONYMOUS_EMAIL", "anonymous@fastfood.local")
        self.max_name_length = int(os.getenv("MAX_NAME_LENGTH", "50"))
        self.min_name_length = int(os.getenv("MIN_NAME_LENGTH", "1"))

        # Webhook Configuration
        self.webhook_url = os.getenv("WEBHOOK_URL", "http://localhost:8000")

    @property
    def cors_config(self) -> dict:
        """Get CORS configuration dictionary"""
        return {
            "allow_origins": self.allowed_origins,
            "allow_credentials": self.allowed_credentials,
            "allow_methods": self.allowed_methods,
            "allow_headers": self.allowed_headers,
        }

    def __str__(self) -> str:
        return f"AppConfig(api_prefix={self.api_prefix}, log_level={self.log_level})"


# Global application configuration instance
app_config = AppConfig()
