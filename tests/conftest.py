import os
import sys
from unittest.mock import patch, MagicMock
import pytest

sys.path.append(os.getcwd())

# Mock boto3 SSM client globally to prevent AWS calls in all tests
@pytest.fixture(scope="session", autouse=True)
def mock_boto3_ssm():
    """Mock boto3 SSM client globally to prevent AWS API calls during tests"""
    with patch("boto3.client") as mock_boto3:
        mock_ssm_client = MagicMock()
        mock_ssm_client.get_parameter.return_value = {"Parameter": {"Value": None}}
        mock_boto3.return_value = mock_ssm_client
        yield mock_boto3
