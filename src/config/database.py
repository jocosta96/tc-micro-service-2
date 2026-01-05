import os
import logging

logger = logging.getLogger(__name__)


class DatabaseConfig:
    """
    Database configuration for PostgreSQL.
    
    Supports both AWS SSM Parameter Store and environment variables.
    Priority: SSM Parameter Store -> Environment Variables -> Default Values

    In Clean Architecture:
    - This is part of the Frameworks & Drivers layer
    - It handles environment-specific configuration
    - It's used by the Interface Adapters layer
    """

    def __init__(self, use_ssm: bool = True, ssm_prefix: str = None):
        """
        Initialize database configuration.
        
        Args:
            use_ssm: Whether to attempt reading from SSM Parameter Store
            ssm_prefix: Prefix for SSM parameter names (if None, uses environment variable)
        """
        self.use_ssm = use_ssm and os.getenv("USE_SSM_PARAMETERS", "true").lower() == "true"
        self.ssm_prefix = ssm_prefix or os.getenv("SSM_PARAMETER_PREFIX", "/fastfood/database/")
        
        # Initialize SSM client if needed
        self._ssm_client = None
        if self.use_ssm:
            try:
                from src.config.aws_ssm import get_ssm_client
                self._ssm_client = get_ssm_client()
                logger.info("SSM client initialized for database configuration")
            except Exception as e:
                logger.warning(f"Failed to initialize SSM client, falling back to environment variables: {e}")
                self.use_ssm = False
        
        # Load configuration
        self.host = self._get_config_value("host", "POSTGRES_HOST", "localhost")
        self.port = int(self._get_config_value("port", "POSTGRES_PORT", "5432"))
        self.database = self._get_config_value("database", "POSTGRES_DB", "fastfood")
        self.username = self._get_config_value("username", "POSTGRES_USER", "postgres")
        self.password = self._get_config_value("password", "POSTGRES_PASSWORD", "password123")
        self.driver = self._get_config_value("driver", "DRIVER_NAME", "postgresql")
        
        logger.info(f"Database configuration loaded - Host: {self.host}, Port: {self.port}, Database: {self.database}")
    
    def _get_config_value(self, ssm_param_name: str, env_var_name: str, default_value: str) -> str:
        """
        Get configuration value with priority: SSM -> Environment -> Default
        
        Args:
            ssm_param_name: Parameter name for SSM (without prefix)
            env_var_name: Environment variable name
            default_value: Default value if neither SSM nor env var is found
            
        Returns:
            Configuration value
        """
        # Try SSM Parameter Store first
        if self.use_ssm and self._ssm_client:
            try:
                ssm_full_name = f"{self.ssm_prefix}{ssm_param_name}"
                ssm_value = self._ssm_client.get_parameter(ssm_full_name, decrypt=True)
                if ssm_value is not None:
                    logger.debug(f"Retrieved {ssm_param_name} from SSM Parameter Store")
                    return ssm_value
            except Exception as e:
                logger.warning(f"Failed to retrieve {ssm_param_name} from SSM: {e}")
        
        # Fallback to environment variable
        env_value = os.getenv(env_var_name)
        if env_value is not None:
            logger.debug(f"Retrieved {ssm_param_name} from environment variable {env_var_name}")
            return env_value
        
        # Use default value
        logger.debug(f"Using default value for {ssm_param_name}")
        return default_value
    
    def reload_from_ssm(self) -> bool:
        """
        Reload configuration from SSM Parameter Store.
        
        Returns:
            True if successfully reloaded from SSM, False otherwise
        """
        if not self.use_ssm or not self._ssm_client:
            logger.warning("SSM not available for configuration reload")
            return False
        
        try:
            # Reload all parameters
            old_host = self.host
            self.host = self._get_config_value("host", "POSTGRES_HOST", "localhost")
            self.port = int(self._get_config_value("port", "POSTGRES_PORT", "5432"))
            self.database = self._get_config_value("database", "POSTGRES_DB", "fastfood")
            self.username = self._get_config_value("username", "POSTGRES_USER", "postgres")
            self.password = self._get_config_value("password", "POSTGRES_PASSWORD", "password123")
            self.driver = self._get_config_value("driver", "DRIVER_NAME", "postgresql")
            
            # Log if configuration changed
            if old_host != self.host:
                logger.info(f"Database configuration reloaded - Host changed from {old_host} to {self.host}")
            else:
                logger.info("Database configuration reloaded from SSM")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to reload configuration from SSM: {e}")
            return False
    
    def get_ssm_parameters(self) -> dict:
        """
        Get all database parameters from SSM for debugging.
        
        Returns:
            Dictionary of parameter names and their SSM paths
        """
        return {
            "host": f"{self.ssm_prefix}host",
            "port": f"{self.ssm_prefix}port",
            "database": f"{self.ssm_prefix}database",
            "username": f"{self.ssm_prefix}username",
            "password": f"{self.ssm_prefix}password",
            "driver": f"{self.ssm_prefix}driver"
        }
    
    def health_check(self) -> dict:
        """
        Check the health of configuration sources.
        
        Returns:
            Dictionary with health status of different sources
        """
        health = {
            "ssm_enabled": self.use_ssm,
            "ssm_available": False,
            "configuration_source": "environment_variables"
        }
        
        if self.use_ssm and self._ssm_client:
            try:
                health["ssm_available"] = self._ssm_client.health_check()
                if health["ssm_available"]:
                    health["configuration_source"] = "ssm_parameter_store"
            except Exception:
                pass
        
        return health

    @property
    def connection_string(self) -> str:
        """Get the PostgreSQL connection string"""
        return f"{self.driver}://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

    @property
    def async_connection_string(self) -> str:
        """Get the async PostgreSQL connection string"""
        return f"{self.driver}+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

    def __str__(self) -> str:
        return f"DatabaseConfig(host={self.host}, port={self.port}, database={self.database}, username={self.username})"


# Global database configuration instance
db_config = DatabaseConfig()
