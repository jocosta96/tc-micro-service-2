"""
Comprehensive tests for DatabaseConfig to increase coverage.
Tests engine creation, table operations, and health checks.
"""

from unittest.mock import MagicMock, patch

from src.config.database import DatabaseConfig


def test_database_config_str_and_health():
    """Given config instance, when str and health_check are called, then both return expected types"""
    config = DatabaseConfig(use_ssm=False)
    s = str(config)
    assert isinstance(s, str)
    health = config.health_check()
    assert isinstance(health, dict)


def test_database_config_connection_strings():
    """Given config instance, when connection_string properties are accessed, then strings are returned"""
    config = DatabaseConfig(use_ssm=False)
    cs = config.connection_string
    acs = config.async_connection_string
    assert isinstance(cs, str)
    assert isinstance(acs, str)
    assert "postgresql://" in cs
    assert "postgresql+asyncpg://" in acs


def test_database_config_get_ssm_parameters():
    """Given config instance, when get_ssm_parameters is called, then dict of SSM paths is returned"""
    config = DatabaseConfig(use_ssm=False)
    params = config.get_ssm_parameters()
    assert isinstance(params, dict)
    assert "host" in params
    assert "port" in params
    assert "database" in params


def test_database_config_with_environment_variables():
    """Given environment variables set, when DatabaseConfig is initialized, then values are loaded from env"""
    with patch.dict(
        "os.environ",
        {
            "POSTGRES_HOST": "testhost",
            "POSTGRES_PORT": "5433",
            "POSTGRES_DB": "testdb",
            "POSTGRES_USER": "testuser",
            "POSTGRES_PASSWORD": "testpass",
            "USE_SSM_PARAMETERS": "false",
        },
    ):
        config = DatabaseConfig(use_ssm=False)

        assert config.host == "testhost"
        assert config.port == 5433
        assert config.database == "testdb"
        assert config.username == "testuser"
        assert config.password == "testpass"


def test_database_config_default_values():
    """Given no env vars or SSM, when DatabaseConfig is initialized, then default values are used"""
    with patch.dict("os.environ", {}, clear=True):
        with patch("os.getenv", return_value=None):
            config = DatabaseConfig(use_ssm=False)

            assert config.host == "localhost"
            assert config.port == 5432
            assert config.database == "fastfood"
            assert config.username == "postgres"


def test_health_check_with_ssm_disabled():
    """Given SSM disabled, when health_check is called, then ssm_available is False"""
    config = DatabaseConfig(use_ssm=False)
    health = config.health_check()

    assert health["ssm_enabled"] is False
    assert health["ssm_available"] is False
    assert health["configuration_source"] == "environment_variables"


def test_health_check_with_ssm_enabled_and_available():
    """Given SSM enabled and available, when health_check is called, then ssm_available is True"""
    mock_ssm = MagicMock()
    mock_ssm.health_check.return_value = True

    with patch("src.config.aws_ssm.get_ssm_client", return_value=mock_ssm):
        config = DatabaseConfig(use_ssm=True)
        health = config.health_check()

        assert health["ssm_available"] is True
        assert health["configuration_source"] == "ssm_parameter_store"


def test_health_check_with_ssm_enabled_but_failed():
    """Given SSM enabled but health check fails, when health_check is called, then ssm_available is False"""
    mock_ssm = MagicMock()
    mock_ssm.health_check.side_effect = Exception("SSM connection failed")

    with patch("src.config.aws_ssm.get_ssm_client", return_value=mock_ssm):
        config = DatabaseConfig(use_ssm=True)
        health = config.health_check()

        assert health["ssm_available"] is False


def test_reload_from_ssm_success():
    """Given SSM client available, when reload_from_ssm is called, then config is reloaded and True returned"""
    mock_ssm = MagicMock()
    mock_ssm.get_parameter.side_effect = lambda param, decrypt: {
        "/fastfood/database/host": "newhost",
        "/fastfood/database/port": "5434",
        "/fastfood/database/database": "newdb",
        "/fastfood/database/username": "newuser",
        "/fastfood/database/password": "newpass",
        "/fastfood/database/driver": "postgresql",
    }.get(param)

    with patch("src.config.aws_ssm.get_ssm_client", return_value=mock_ssm):
        config = DatabaseConfig(use_ssm=True)

        result = config.reload_from_ssm()

        assert result is True
        assert config.host == "newhost"
        assert config.port == 5434


def test_reload_from_ssm_when_disabled():
    """Given SSM disabled, when reload_from_ssm is called, then False is returned"""
    config = DatabaseConfig(use_ssm=False)

    result = config.reload_from_ssm()

    assert result is False


def test_reload_from_ssm_with_error():
    """Given SSM disabled after init, when reload_from_ssm is called, then False is returned"""
    # Create config with SSM enabled and initial values
    mock_ssm = MagicMock()

    # Initial config creation succeeds
    def initial_get(param, decrypt=False):
        param_name = param.split("/")[-1]
        return {
            "host": "initial",
            "port": "5432",
            "database": "db",
            "username": "user",
            "password": "pass",
            "driver": "postgresql",
        }.get(param_name)

    mock_ssm.get_parameter.side_effect = initial_get

    with patch("src.config.aws_ssm.get_ssm_client", return_value=mock_ssm):
        config = DatabaseConfig(use_ssm=True)

        # Disable SSM to simulate unavailability
        config.use_ssm = False

        result = config.reload_from_ssm()

        # Should return False when SSM is disabled
        assert result is False


def test_get_config_value_priority_ssm_over_env():
    """Given both SSM and env var exist, when config is initialized, then SSM values take priority"""
    mock_ssm = MagicMock()

    # Mock SSM to return values for all database parameters
    def mock_get_param(param, decrypt=False):
        param_map = {
            "/fastfood/database/host": "ssm_host",
            "/fastfood/database/port": "5433",
            "/fastfood/database/database": "ssm_db",
            "/fastfood/database/username": "ssm_user",
            "/fastfood/database/password": "ssm_pass",
            "/fastfood/database/driver": "postgresql",
        }
        return param_map.get(param)

    mock_ssm.get_parameter.side_effect = mock_get_param

    # Set env vars that should be overridden
    with patch.dict(
        "os.environ", {"POSTGRES_HOST": "env_host", "POSTGRES_PORT": "5432"}
    ):
        with patch("src.config.aws_ssm.get_ssm_client", return_value=mock_ssm):
            config = DatabaseConfig(use_ssm=True)

            # Verify SSM values were used instead of env vars
            assert config.host == "ssm_host"
            assert config.port == 5433


def test_get_config_value_falls_back_to_env():
    """Given SSM fails but env var exists, when getting config value, then env var is used"""
    mock_ssm = MagicMock()
    mock_ssm.get_parameter.return_value = None

    with patch.dict("os.environ", {"TEST_VAR": "env_value"}):
        with patch("src.config.aws_ssm.get_ssm_client", return_value=mock_ssm):
            config = DatabaseConfig(use_ssm=True)
            config._ssm_client = mock_ssm

            value = config._get_config_value("test", "TEST_VAR", "default")

            assert value == "env_value"


def test_get_config_value_uses_default():
    """Given neither SSM nor env var exist, when getting config value, then default is used"""
    config = DatabaseConfig(use_ssm=False)

    with patch.dict("os.environ", {}, clear=True):
        with patch("os.getenv", return_value=None):
            value = config._get_config_value("test", "TEST_VAR", "default_value")

            assert value == "default_value"


def test_connection_string_format():
    """Given config values, when connection_string is accessed, then proper format is returned"""
    with patch.dict(
        "os.environ",
        {
            "POSTGRES_HOST": "myhost",
            "POSTGRES_PORT": "5432",
            "POSTGRES_DB": "mydb",
            "POSTGRES_USER": "myuser",
            "POSTGRES_PASSWORD": "mypass",
            "DRIVER_NAME": "postgresql",
            "USE_SSM_PARAMETERS": "false",
        },
    ):
        config = DatabaseConfig(use_ssm=False)
        cs = config.connection_string

        assert cs == "postgresql://myuser:mypass@myhost:5432/mydb"


def test_async_connection_string_format():
    """Given config values, when async_connection_string is accessed, then proper asyncpg format is returned"""
    with patch.dict(
        "os.environ",
        {
            "POSTGRES_HOST": "myhost",
            "POSTGRES_PORT": "5432",
            "POSTGRES_DB": "mydb",
            "POSTGRES_USER": "myuser",
            "POSTGRES_PASSWORD": "mypass",
            "DRIVER_NAME": "postgresql",
            "USE_SSM_PARAMETERS": "false",
        },
    ):
        config = DatabaseConfig(use_ssm=False)
        acs = config.async_connection_string

        assert acs == "postgresql+asyncpg://myuser:mypass@myhost:5432/mydb"
