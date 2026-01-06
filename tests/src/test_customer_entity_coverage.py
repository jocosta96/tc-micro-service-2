import pytest
from src.entities.customer import Customer
from src.entities.value_objects.name import Name
from src.entities.value_objects.email import Email
from src.entities.value_objects.document import Document


class TestCustomer:
    from src.entities.value_objects.name import Name
    from src.entities.value_objects.email import Email
    from src.entities.value_objects.document import Document

    def test_create_valid_customer(self):
        # Given dados válidos
        customer = Customer(
            first_name=Name("João"),
            last_name=Name("Silva"),
            email=Email("joao@email.com"),
            document=Document("12345678909"),
            is_active=True,
            is_anonymous=False,
            internal_id=1,
        )
        # Then instancia corretamente
        assert customer.internal_id == 1
        assert str(customer.first_name) == "João"
        assert str(customer.email) == "joao@email.com"
        assert str(customer.document) == "12345678909"

    def test_create_invalid_customer_raises(self):
        # Given dados inválidos (email inválido)
        from src.entities.value_objects.name import Name
        from src.entities.value_objects.email import Email
        from src.entities.value_objects.document import Document

        with pytest.raises(Exception):
            Customer(
                first_name=Name("Maria"),
                last_name=Name("Oliveira"),
                email=Email("invalid-email"),
                document=Document("12345678909"),
                is_active=True,
                is_anonymous=False,
                internal_id=2,
            )

    def test_edge_methods(self):
        # Given cliente válido
        from src.entities.value_objects.name import Name
        from src.entities.value_objects.email import Email
        from src.entities.value_objects.document import Document

        customer = Customer(
            first_name=Name("Edge"),
            last_name=Name("Case"),
            email=Email("edge@email.com"),
            document=Document("12345678909"),
            is_active=True,
            is_anonymous=False,
            internal_id=3,
        )
        # When chamar __str__
        s = str(customer)
        # Then retorna string representativa
        assert "Edge" in s

    def test_invalid_document_raises(self):
        # Given documento inválido
        from src.entities.value_objects.name import Name
        from src.entities.value_objects.email import Email
        from src.entities.value_objects.document import Document

        with pytest.raises(Exception):
            Customer(
                first_name=Name("Doc"),
                last_name=Name("Test"),
                email=Email("doc@email.com"),
                document=Document("abc"),
                is_active=True,
                is_anonymous=False,
                internal_id=4,
            )
