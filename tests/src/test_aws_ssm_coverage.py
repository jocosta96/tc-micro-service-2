import pytest
from unittest.mock import patch, MagicMock
from src.config.aws_ssm import SSMParameterStore


class TestSSMParameterStore:
    @patch("src.config.aws_ssm.boto3.client")
    def test_get_parameter_success(self, mock_boto):
        # Given parâmetro existe
        mock_client = MagicMock()
        mock_client.get_parameter.return_value = {"Parameter": {"Value": "ok"}}
        mock_boto.return_value = mock_client
        ssm = SSMParameterStore()
        # When buscar
        val = ssm.get_parameter("param")
        # Then retorna valor
        assert val == "ok"

    @patch("src.config.aws_ssm.boto3.client")
    def test_get_parameter_not_found(self, mock_boto):
        # Given parâmetro não existe
        mock_client = MagicMock()
        mock_client.get_parameter.side_effect = Exception("NotFound")
        mock_boto.return_value = mock_client
        ssm = SSMParameterStore()
        # When buscar, Then retorna None/erro
        with pytest.raises(Exception):
            ssm.get_parameter("param")

    @patch("src.config.aws_ssm.boto3.client")
    def test_get_parameter_aws_error(self, mock_boto):
        # Given erro AWS
        mock_boto.side_effect = Exception("AWS error")
        # When inicializa, Then lança exceção
        with pytest.raises(Exception) as excinfo:
            SSMParameterStore()
        # Verifica mensagem da exceção
        assert "AWS error" in str(excinfo.value)
