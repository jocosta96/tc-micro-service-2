import pytest
from src.entities.value_objects.email import Email


class TestEmail:
    def test_valid_email(self):
        # Given email válido
        email = Email("valid@email.com")
        # Then aceita
        assert email.value == "valid@email.com"

    def test_invalid_email_raises(self):
        # Given email inválido
        with pytest.raises(Exception):
            Email("invalid-email")

    def test_empty_email_allowed(self):
        # Given email vazio
        email = Email("")
        # Then aceita
        assert email.value == ""
