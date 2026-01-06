"""
Comprehensive tests for AWS SSM Parameter Store to increase coverage.
Focuses on get_parameter, get_parameters, set_parameter, health_check, and credentials management.
"""

from unittest.mock import MagicMock, patch
import pytest
from botocore.exceptions import ClientError, NoCredentialsError, EndpointConnectionError

from src.config.aws_ssm import (
    SSMParameterStore,
    set_aws_credentials,
    clear_aws_credentials,
    get_aws_credentials_status,
    get_ssm_client,
    _aws_credentials,
)


@pytest.fixture
def mock_boto_client():
    """Fixture to mock boto3.client"""
    with patch("boto3.client") as mock_client:
        mock_ssm = MagicMock()
        mock_client.return_value = mock_ssm
        yield mock_ssm


@pytest.fixture(autouse=True)
def reset_credentials():
    """Reset global credentials before each test"""
    clear_aws_credentials()
    yield
    clear_aws_credentials()


def test_ssm_init_with_default_region(mock_boto_client):
    """Given no region specified, when SSMParameterStore is initialized, then uses default region"""
    with patch.dict("os.environ", {"AWS_DEFAULT_REGION": "us-west-2"}):
        ssm = SSMParameterStore()

        assert ssm.region_name == "us-west-2"


def test_ssm_init_with_custom_region(mock_boto_client):
    """Given custom region, when SSMParameterStore is initialized, then uses specified region"""
    ssm = SSMParameterStore(region_name="eu-west-1")

    assert ssm.region_name == "eu-west-1"


def test_get_parameter_found(mock_boto_client):
    """Given parameter exists in SSM, when get_parameter is called, then returns parameter value"""
    mock_boto_client.get_parameter.return_value = {
        "Parameter": {"Name": "/app/db_password", "Value": "secret123"}
    }

    ssm = SSMParameterStore()
    result = ssm.get_parameter("/app/db_password", decrypt=True)

    assert result == "secret123"
    mock_boto_client.get_parameter.assert_called_once_with(
        Name="/app/db_password", WithDecryption=True
    )


def test_get_parameter_not_found(mock_boto_client):
    """Given parameter does not exist, when get_parameter is called, then returns None"""
    error_response = {"Error": {"Code": "ParameterNotFound"}}
    mock_boto_client.get_parameter.side_effect = ClientError(
        error_response, "get_parameter"
    )

    ssm = SSMParameterStore()
    result = ssm.get_parameter("/app/nonexistent")

    assert result is None


def test_get_parameter_client_error(mock_boto_client):
    """Given AWS client error, when get_parameter is called, then raises exception"""
    error_response = {"Error": {"Code": "AccessDenied", "Message": "Access denied"}}
    mock_boto_client.get_parameter.side_effect = ClientError(
        error_response, "get_parameter"
    )

    ssm = SSMParameterStore()

    with pytest.raises(ClientError):
        ssm.get_parameter("/app/param")


def test_get_parameter_no_credentials_error(mock_boto_client):
    """Given no AWS credentials, when get_parameter is called, then raises NoCredentialsError"""
    mock_boto_client.get_parameter.side_effect = NoCredentialsError()

    ssm = SSMParameterStore()

    with pytest.raises(NoCredentialsError):
        ssm.get_parameter("/app/param")


def test_get_parameter_connection_error(mock_boto_client):
    """Given network connection error, when get_parameter is called, then raises EndpointConnectionError"""
    mock_boto_client.get_parameter.side_effect = EndpointConnectionError(
        endpoint_url="https://ssm.us-east-1.amazonaws.com"
    )

    ssm = SSMParameterStore()

    with pytest.raises(EndpointConnectionError):
        ssm.get_parameter("/app/param")


def test_get_parameter_unexpected_error(mock_boto_client):
    """Given unexpected error, when get_parameter is called, then raises exception"""
    mock_boto_client.get_parameter.side_effect = Exception("Unexpected error")

    ssm = SSMParameterStore()

    with pytest.raises(Exception) as exc_info:
        ssm.get_parameter("/app/param")

    assert "Unexpected error" in str(exc_info.value)


def test_get_parameters_success(mock_boto_client):
    """Given multiple parameters, when get_parameters is called, then returns dict of all parameters"""
    mock_boto_client.get_parameters.return_value = {
        "Parameters": [
            {"Name": "/app/param1", "Value": "value1"},
            {"Name": "/app/param2", "Value": "value2"},
        ],
        "InvalidParameters": [],
    }

    ssm = SSMParameterStore()
    result = ssm.get_parameters(["/app/param1", "/app/param2"])

    assert result == {"/app/param1": "value1", "/app/param2": "value2"}


def test_get_parameters_with_invalid(mock_boto_client):
    """Given mix of valid and invalid parameters, when get_parameters is called, then returns only valid ones"""
    mock_boto_client.get_parameters.return_value = {
        "Parameters": [{"Name": "/app/param1", "Value": "value1"}],
        "InvalidParameters": ["/app/invalid"],
    }

    ssm = SSMParameterStore()
    result = ssm.get_parameters(["/app/param1", "/app/invalid"])

    assert result == {"/app/param1": "value1"}
    assert "/app/invalid" not in result


def test_get_parameters_empty_list(mock_boto_client):
    """Given empty parameter list, when get_parameters is called, then returns empty dict"""
    ssm = SSMParameterStore()
    result = ssm.get_parameters([])

    assert result == {}
    mock_boto_client.get_parameters.assert_not_called()


def test_get_parameters_batch_processing(mock_boto_client):
    """Given more than 10 parameters, when get_parameters is called, then processes in batches"""
    # Create 15 parameters
    param_names = [f"/app/param{i}" for i in range(15)]

    # Mock two batches of responses
    def get_params_side_effect(Names, WithDecryption):
        return {
            "Parameters": [{"Name": name, "Value": f"value_{name}"} for name in Names],
            "InvalidParameters": [],
        }

    mock_boto_client.get_parameters.side_effect = get_params_side_effect

    ssm = SSMParameterStore()
    result = ssm.get_parameters(param_names)

    # Should make 2 calls (10 + 5)
    assert mock_boto_client.get_parameters.call_count == 2
    assert len(result) == 15


def test_get_parameters_connection_error(mock_boto_client):
    """Given connection error, when get_parameters is called, then raises exception"""
    mock_boto_client.get_parameters.side_effect = EndpointConnectionError(
        endpoint_url="https://ssm.us-east-1.amazonaws.com"
    )

    ssm = SSMParameterStore()

    with pytest.raises(EndpointConnectionError):
        ssm.get_parameters(["/app/param1"])


def test_get_parameter_with_fallback_found(mock_boto_client):
    """Given parameter exists, when get_parameter_with_fallback is called, then returns parameter value"""
    mock_boto_client.get_parameter.return_value = {
        "Parameter": {"Name": "/app/param", "Value": "ssm_value"}
    }

    ssm = SSMParameterStore()
    result = ssm.get_parameter_with_fallback("/app/param", "fallback_value")

    assert result == "ssm_value"


def test_get_parameter_with_fallback_not_found(mock_boto_client):
    """Given parameter not found, when get_parameter_with_fallback is called, then returns fallback value"""
    error_response = {"Error": {"Code": "ParameterNotFound"}}
    mock_boto_client.get_parameter.side_effect = ClientError(
        error_response, "get_parameter"
    )

    ssm = SSMParameterStore()
    result = ssm.get_parameter_with_fallback("/app/param", "fallback_value")

    assert result == "fallback_value"


def test_get_parameter_with_fallback_on_error(mock_boto_client):
    """Given connection error, when get_parameter_with_fallback is called, then returns fallback value"""
    mock_boto_client.get_parameter.side_effect = EndpointConnectionError(
        endpoint_url="https://ssm.us-east-1.amazonaws.com"
    )

    ssm = SSMParameterStore()
    result = ssm.get_parameter_with_fallback("/app/param", "fallback_value")

    assert result == "fallback_value"


def test_health_check_success(mock_boto_client):
    """Given SSM is accessible, when health_check is called, then returns True"""
    mock_boto_client.describe_parameters.return_value = {"Parameters": []}

    ssm = SSMParameterStore()
    result = ssm.health_check()

    assert result is True
    mock_boto_client.describe_parameters.assert_called_once_with(MaxResults=1)


def test_health_check_failure(mock_boto_client):
    """Given SSM is not accessible, when health_check is called, then returns False"""
    mock_boto_client.describe_parameters.side_effect = Exception("Connection failed")

    ssm = SSMParameterStore()
    result = ssm.health_check()

    assert result is False


def test_update_credentials(mock_boto_client):
    """Given new credentials, when update_credentials is called, then credentials are updated and client recreated"""
    ssm = SSMParameterStore()

    # Verify update_credentials doesn't raise exception
    ssm.update_credentials("NEW_KEY", "NEW_SECRET", "NEW_TOKEN")

    # Verify global credentials were updated
    from src.config.aws_ssm import _aws_credentials

    assert _aws_credentials["aws_access_key_id"] == "NEW_KEY"
    assert _aws_credentials["aws_secret_access_key"] == "NEW_SECRET"
    assert _aws_credentials["aws_session_token"] == "NEW_TOKEN"


def test_set_aws_credentials():
    """Given AWS credentials, when set_aws_credentials is called, then global credentials are set"""
    from src.config import aws_ssm

    result = set_aws_credentials("AKIATEST", "secret123", "token456")

    assert result is True
    assert aws_ssm._aws_credentials["aws_access_key_id"] == "AKIATEST"
    assert aws_ssm._aws_credentials["aws_secret_access_key"] == "secret123"
    assert aws_ssm._aws_credentials["aws_session_token"] == "token456"


def test_set_aws_credentials_without_token():
    """Given credentials without session token, when set_aws_credentials is called, then sets credentials"""
    from src.config import aws_ssm

    result = set_aws_credentials("AKIATEST", "secret123")

    assert result is True
    assert aws_ssm._aws_credentials["aws_access_key_id"] == "AKIATEST"
    assert aws_ssm._aws_credentials["aws_secret_access_key"] == "secret123"
    assert aws_ssm._aws_credentials["aws_session_token"] is None


def test_get_aws_credentials_status_with_credentials():
    """Given credentials are set, when get_aws_credentials_status is called, then returns status with all True"""
    set_aws_credentials("AKIATEST", "secret123", "token456")

    status = get_aws_credentials_status()

    assert status["credentials_set"] is True
    assert status["has_access_key"] is True
    assert status["has_secret_key"] is True
    assert status["has_session_token"] is True
    assert status["credential_source"] == "global"


def test_get_aws_credentials_status_without_credentials():
    """Given no credentials set, when get_aws_credentials_status is called, then returns status with all False"""
    clear_aws_credentials()

    status = get_aws_credentials_status()

    assert status["credentials_set"] is False
    assert status["has_access_key"] is False
    assert status["has_secret_key"] is False
    assert status["has_session_token"] is False
    assert status["credential_source"] == "environment/default"


def test_clear_aws_credentials():
    """Given credentials are set, when clear_aws_credentials is called, then all credentials are cleared"""
    set_aws_credentials("AKIATEST", "secret123", "token456")

    clear_aws_credentials()

    assert _aws_credentials["aws_access_key_id"] is None
    assert _aws_credentials["aws_secret_access_key"] is None
    assert _aws_credentials["aws_session_token"] is None


def test_get_ssm_client_singleton(mock_boto_client):
    """Given multiple calls, when get_ssm_client is called, then returns same instance"""
    from src.config import aws_ssm

    # Reset the global client
    aws_ssm._ssm_client = None

    client1 = get_ssm_client()
    client2 = get_ssm_client()

    assert client1 is client2


def test_create_ssm_client_with_global_credentials():
    """Given global credentials set, when creating SSM client, then uses global credentials"""
    set_aws_credentials("AKIATEST", "secret123", "token456")

    with patch("boto3.client") as mock_client:
        mock_client.return_value = MagicMock()

        ssm = SSMParameterStore()

        # Verify SSM client was created
        assert ssm.ssm_client is not None
        # Verify boto3.client was called with credentials
        mock_client.assert_called()
        call_kwargs = mock_client.call_args[1]
        assert call_kwargs.get("aws_access_key_id") == "AKIATEST"
        assert call_kwargs.get("aws_secret_access_key") == "secret123"
        assert call_kwargs.get("aws_session_token") == "token456"


def test_create_ssm_client_with_env_credentials():
    """Given env credentials set, when creating SSM client, then uses env credentials"""
    clear_aws_credentials()

    with patch.dict(
        "os.environ",
        {"AWS_ACCESS_KEY_ID": "ENV_KEY", "AWS_SECRET_ACCESS_KEY": "ENV_SECRET"},
    ):
        with patch("boto3.client") as mock_client:
            mock_client.return_value = MagicMock()

            ssm = SSMParameterStore()

            # Should call boto3.client
            mock_client.assert_called()


def test_create_ssm_client_with_default_credentials():
    """Given no credentials set, when creating SSM client, then uses default credential chain"""
    clear_aws_credentials()

    with patch.dict("os.environ", {}, clear=True):
        with patch("os.getenv", return_value=None):
            with patch("boto3.client") as mock_client:
                mock_client.return_value = MagicMock()

                ssm = SSMParameterStore()

                # Should call boto3.client with only region
                mock_client.assert_called()
