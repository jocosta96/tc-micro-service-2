from src.config.database import DatabaseConfig

def test_database_config_str_and_health():
    config = DatabaseConfig(use_ssm=False)
    s = str(config)
    assert isinstance(s, str)
    health = config.health_check()
    assert isinstance(health, dict)

def test_database_config_connection_strings():
    config = DatabaseConfig(use_ssm=False)
    cs = config.connection_string  # method, not property
    if callable(cs):
        cs = cs()
    acs = config.async_connection_string  # property
    assert isinstance(cs, str)
    assert isinstance(acs, str)

def test_database_config_get_ssm_parameters():
    config = DatabaseConfig(use_ssm=False)
    params = config.get_ssm_parameters()
    assert isinstance(params, dict)
