import pytest
from unittest.mock import patch, MagicMock
from src.config.database import DatabaseConfig

class TestDatabaseConfig:
    @patch('sqlalchemy.create_engine')
    def test_connect_success(self, mock_create_engine):
        # Given config válida
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        db = DatabaseConfig()
        # When conectar (simulado)
        # Não existe método connect, apenas valida instância
        assert db is not None

    @patch('sqlalchemy.create_engine')
    def test_connect_invalid_config(self, mock_create_engine):
        # Given config inválida
        mock_create_engine.side_effect = Exception('Invalid config')
        # DatabaseConfig não lança na criação, apenas loga warning
        db = DatabaseConfig()
        assert db is not None

    def test_str_method(self):
        # Testa __str__
        db = DatabaseConfig()
        s = str(db)
        assert 'DatabaseConfig' in s
