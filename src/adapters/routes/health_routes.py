from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing_extensions import Annotated
from src.adapters.di.container import container
from src.config.database import db_config
from src.config.aws_ssm import set_aws_credentials, get_aws_credentials_status, clear_aws_credentials
from src.security.http_auth import check_credentials

health_router = APIRouter(tags=["health"])

class AWSCredentials(BaseModel):
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_session_token: str = None


@health_router.get("/health")
def health_check():
    """Health check endpoint for Kubernetes probes"""
    return {"status": "healthy", "message": "Application is running"}


@health_router.get("/health/db")
def database_health_check():
    """Database health check endpoint"""
    try:
        # Test database connection
        repository = container.customer_repository
        # Try to get anonymous customer as a simple DB test
        repository.get_anonymous_customer()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}


@health_router.get("/health/config")
def configuration_health_check():
    """Configuration health check endpoint - shows SSM status and configuration sources"""
    try:
        config_health = db_config.health_check()
        
        response = {
            "status": "healthy",
            "configuration": {
                "ssm_enabled": config_health["ssm_enabled"],
                "ssm_available": config_health["ssm_available"], 
                "primary_source": config_health["configuration_source"],
                "database_name": db_config.database
            },
            "aws_credentials": get_aws_credentials_status()
        }
        
        if config_health["ssm_enabled"]:
            response["configuration"]["ssm_parameters"] = db_config.get_ssm_parameters()
        
        return response
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "configuration": {
                "error": str(e),
                "ssm_enabled": False,
                "primary_source": "unknown"
            }
        }


@health_router.post("/health/config/reload")
def reload_configuration():
    """Reload configuration from SSM Parameter Store (admin endpoint)"""
    try:
        success = db_config.reload_from_ssm()
        
        if success:
            return {
                "status": "success",
                "message": "Configuration reloaded from SSM Parameter Store",
                "new_config": {
                    "database_host": db_config.host,
                    "database_port": db_config.port, 
                    "database_name": db_config.database
                }
            }
        else:
            return {
                "status": "failed",
                "message": "Failed to reload configuration from SSM",
                "current_config": {
                    "database_host": db_config.host,
                    "database_port": db_config.port,
                    "database_name": db_config.database
                }
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error reloading configuration: {str(e)}"
        }


@health_router.post("/health/aws-credentials")
def set_aws_credentials_endpoint(
    credentials: AWSCredentials,
    login: Annotated[str, Depends(check_credentials)]
):
    """Set AWS credentials for SSM access (for labs environment with temporary credentials)
    
    Requires HTTP Basic Auth (admin credentials)
    """
    try:
        success = set_aws_credentials(
            credentials.aws_access_key_id,
            credentials.aws_secret_access_key,
            credentials.aws_session_token
        )
        
        if success:
            return {
                "status": "success",
                "message": "AWS credentials set successfully",
                "credentials_status": get_aws_credentials_status()
            }
        else:
            return {
                "status": "failed",
                "message": "Failed to set AWS credentials"
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error setting AWS credentials: {str(e)}")


@health_router.get("/health/aws-credentials")
def get_aws_credentials_status_endpoint(
    login: Annotated[str, Depends(check_credentials)]
):
    """Get current AWS credentials status
    
    Requires HTTP Basic Auth (admin credentials)
    """
    try:
        return {
            "status": "success",
            "aws_credentials": get_aws_credentials_status()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting AWS credentials status: {str(e)}")


@health_router.delete("/health/aws-credentials")  
def clear_aws_credentials_endpoint(
    login: Annotated[str, Depends(check_credentials)]
):
    """Clear AWS credentials
    
    Requires HTTP Basic Auth (admin credentials)
    """
    try:
        clear_aws_credentials()
        return {
            "status": "success",
            "message": "AWS credentials cleared successfully",
            "credentials_status": get_aws_credentials_status()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing AWS credentials: {str(e)}")
