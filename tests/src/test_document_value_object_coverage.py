import pytest
from src.entities.value_objects.document import Document

class TestDocument:
    def test_valid_document(self):
        # Given documento válido
        doc = Document('12345678909')
        # Then aceita
        assert doc.value == '12345678909'

    def test_invalid_document_raises(self):
        # Given documento inválido
        with pytest.raises(Exception):
            Document('abc')

    def test_empty_document_allowed(self):
        # Given documento vazio
        doc = Document('')
        # Then aceita
        assert doc.value == ''
