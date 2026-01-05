import os
import boto3
import logging
from typing import Dict, Optional
from botocore.exceptions import ClientError, NoCredentialsError, EndpointConnectionError

logger = logging.getLogger(__name__)

# Global AWS credentials storage
_aws_credentials = {
    'aws_access_key_id': None,
    'aws_secret_access_key': None,
    'aws_session_token': None
}


class SSMParameterStore:
    """
    AWS Systems Manager Parameter Store client.
    
    In Clean Architecture:
    - This is part of the Frameworks & Drivers layer
    - It handles external AWS services integration
    - It provides a clean interface for parameter retrieval
    """
    
    def __init__(self, region_name: str = None):
        """
        Initialize SSM client.
        
        Args:
            region_name: AWS region name. If None, uses default region from environment/config.
        """
        self.region_name = region_name or os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        
        try:
            self.ssm_client = self._create_ssm_client()
            logger.info(f"Initialized SSM client for region: {self.region_name}")
        except Exception as e:
            logger.error(f"Failed to initialize SSM client: {e}")
            raise
    
    def _create_ssm_client(self):
        """Create SSM client with appropriate credentials."""
        # Try global credentials first (for labs environment)
        if all(_aws_credentials.values()):
            logger.info("Using global AWS credentials")
            return boto3.client(
                'ssm',
                region_name=self.region_name,
                aws_access_key_id=_aws_credentials['aws_access_key_id'],
                aws_secret_access_key=_aws_credentials['aws_secret_access_key'],
                aws_session_token=_aws_credentials['aws_session_token']
            )
        
        # Try environment variables (traditional approach)
        if all([os.getenv('AWS_ACCESS_KEY_ID'), os.getenv('AWS_SECRET_ACCESS_KEY')]):
            logger.info("Using environment variable AWS credentials")
            return boto3.client('ssm', region_name=self.region_name)
        
        # Fall back to default credentials (IAM roles, etc.)
        logger.info("Using default AWS credentials chain")
        return boto3.client('ssm', region_name=self.region_name)
    
    def update_credentials(self, aws_access_key_id: str, aws_secret_access_key: str, aws_session_token: str = None):
        """
        Update AWS credentials and recreate SSM client.
        
        Args:
            aws_access_key_id: AWS access key ID
            aws_secret_access_key: AWS secret access key
            aws_session_token: AWS session token (optional, required for temporary credentials)
        """
        global _aws_credentials
        
        _aws_credentials['aws_access_key_id'] = aws_access_key_id
        _aws_credentials['aws_secret_access_key'] = aws_secret_access_key
        _aws_credentials['aws_session_token'] = aws_session_token
        
        # Recreate the SSM client with new credentials
        try:
            self.ssm_client = self._create_ssm_client()
            logger.info("Successfully updated AWS credentials and recreated SSM client")
        except Exception as e:
            logger.error(f"Failed to recreate SSM client with new credentials: {e}")
            raise
    
    def get_parameter(self, parameter_name: str, decrypt: bool = True) -> Optional[str]:
        """
        Retrieve a single parameter from SSM Parameter Store.
        
        Args:
            parameter_name: The name of the parameter to retrieve
            decrypt: Whether to decrypt SecureString parameters
            
        Returns:
            Parameter value or None if not found
            
        Raises:
            Exception: If there's an error retrieving the parameter
        """
        try:
            response = self.ssm_client.get_parameter(
                Name=parameter_name,
                WithDecryption=decrypt
            )
            value = response['Parameter']['Value']
            logger.debug(f"Successfully retrieved parameter: {parameter_name}")
            return value
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code')
            if error_code == 'ParameterNotFound':
                logger.warning(f"Parameter not found: {parameter_name}")
                return None
            else:
                logger.error(f"Error retrieving parameter {parameter_name}: {e}")
                raise
                
        except (NoCredentialsError, EndpointConnectionError) as e:
            logger.error(f"AWS configuration error when retrieving {parameter_name}: {e}")
            raise
            
        except Exception as e:
            logger.error(f"Unexpected error retrieving parameter {parameter_name}: {e}")
            raise
    
    def get_parameters(self, parameter_names: list, decrypt: bool = True) -> Dict[str, str]:
        """
        Retrieve multiple parameters from SSM Parameter Store in batch.
        
        Args:
            parameter_names: List of parameter names to retrieve
            decrypt: Whether to decrypt SecureString parameters
            
        Returns:
            Dictionary mapping parameter names to values
            
        Raises:
            Exception: If there's an error retrieving parameters
        """
        if not parameter_names:
            return {}
            
        try:
            # SSM get_parameters has a limit of 10 parameters per call
            parameters = {}
            
            for i in range(0, len(parameter_names), 10):
                batch = parameter_names[i:i+10]
                
                response = self.ssm_client.get_parameters(
                    Names=batch,
                    WithDecryption=decrypt
                )
                
                for param in response.get('Parameters', []):
                    parameters[param['Name']] = param['Value']
                    
                # Log any invalid parameters
                for invalid_param in response.get('InvalidParameters', []):
                    logger.warning(f"Invalid or not found parameter: {invalid_param}")
                    
            logger.debug(f"Successfully retrieved {len(parameters)} parameters")
            return parameters
            
        except (NoCredentialsError, EndpointConnectionError) as e:
            logger.error(f"AWS configuration error when retrieving parameters: {e}")
            raise
            
        except Exception as e:
            logger.error(f"Unexpected error retrieving parameters: {e}")
            raise
    
    def get_parameter_with_fallback(self, parameter_name: str, fallback_value: str, decrypt: bool = True) -> str:
        """
        Retrieve a parameter with a fallback value if not found.
        
        Args:
            parameter_name: The name of the parameter to retrieve
            fallback_value: Value to return if parameter is not found
            decrypt: Whether to decrypt SecureString parameters
            
        Returns:
            Parameter value or fallback value
        """
        try:
            value = self.get_parameter(parameter_name, decrypt)
            if value is not None:
                return value
            else:
                logger.info(f"Parameter {parameter_name} not found, using fallback value")
                return fallback_value
                
        except Exception as e:
            logger.warning(f"Error retrieving parameter {parameter_name}, using fallback: {e}")
            return fallback_value
    
    def health_check(self) -> bool:
        """
        Check if SSM service is accessible.
        
        Returns:
            True if SSM is accessible, False otherwise
        """
        try:
            # Try to make a simple call to verify connectivity
            self.ssm_client.describe_parameters(MaxResults=1)
            return True
        except Exception as e:
            logger.error(f"SSM health check failed: {e}")
            return False


# Global SSM client instance
_ssm_client = None

def set_aws_credentials(aws_access_key_id: str, aws_secret_access_key: str, aws_session_token: str = None) -> bool:
    """
    Set global AWS credentials for SSM access (for labs environment).
    
    Args:
        aws_access_key_id: AWS access key ID
        aws_secret_access_key: AWS secret access key
        aws_session_token: AWS session token (required for temporary credentials)
        
    Returns:
        True if credentials were set successfully, False otherwise
    """
    global _aws_credentials, _ssm_client
    
    try:
        # Update global credentials
        _aws_credentials['aws_access_key_id'] = aws_access_key_id
        _aws_credentials['aws_secret_access_key'] = aws_secret_access_key
        _aws_credentials['aws_session_token'] = aws_session_token
        
        # Update existing SSM client if it exists
        if _ssm_client:
            _ssm_client.update_credentials(aws_access_key_id, aws_secret_access_key, aws_session_token)
        
        logger.info("Global AWS credentials updated successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to set AWS credentials: {e}")
        return False

def get_aws_credentials_status() -> dict:
    """
    Get current AWS credentials status.
    
    Returns:
        Dictionary with credentials status
    """
    return {
        'credentials_set': all(_aws_credentials.values()),
        'has_access_key': bool(_aws_credentials['aws_access_key_id']),
        'has_secret_key': bool(_aws_credentials['aws_secret_access_key']),
        'has_session_token': bool(_aws_credentials['aws_session_token']),
        'credential_source': 'global' if all(_aws_credentials.values()) else 'environment/default'
    }

def clear_aws_credentials():
    """Clear global AWS credentials."""
    global _aws_credentials
    _aws_credentials = {
        'aws_access_key_id': None,
        'aws_secret_access_key': None,
        'aws_session_token': None
    }
    logger.info("Global AWS credentials cleared")

def get_ssm_client() -> SSMParameterStore:
    """
    Get or create a global SSM client instance.
    
    Returns:
        SSMParameterStore instance
    """
    global _ssm_client
    if _ssm_client is None:
        _ssm_client = SSMParameterStore()
    return _ssm_client
