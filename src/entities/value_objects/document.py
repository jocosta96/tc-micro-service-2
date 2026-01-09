from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Document:
    """
    Document value object that represents a valid Brazilian CPF number.

    This is a value object because:
    - It's immutable (frozen=True)
    - It validates itself during creation
    - It has no identity, only value
    - Two documents are equal if they have the same value
    """

    value: str

    def __post_init__(self):
        """Validate the CPF during object creation"""
        if self.value and not self._is_valid_cpf(self.value):
            raise ValueError(f"Invalid CPF: {self.value}")

    @staticmethod
    def _is_valid_cpf(cpf: str) -> bool:
        """Validate Brazilian CPF format and check digits"""
        if not cpf or cpf.strip() == "":
            return True  # Allow empty documents for anonymous customers

        # Remove non-digits
        cpf_clean = re.sub(r"\D", "", cpf)

        # Check if it has exactly 11 digits
        if not re.fullmatch(r"\d{11}", cpf_clean):
            return False

        # Check if all digits are the same (invalid CPF)
        if len(set(cpf_clean)) == 1:
            return False

        # Validate check digits
        numbers = [int(d) for d in cpf_clean]

        # First check digit
        sum1 = sum(a * b for a, b in zip(numbers[:9], range(10, 1, -1)))
        check1 = (sum1 * 10) % 11
        if check1 == 10:
            check1 = 0
        if numbers[9] != check1:
            return False

        # Second check digit
        sum2 = sum(a * b for a, b in zip(numbers[:10], range(11, 1, -1)))
        check2 = (sum2 * 10) % 11
        if check2 == 10:
            check2 = 0
        if numbers[10] != check2:
            return False

        return True

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"Document('{self.value}')"

    @classmethod
    def create(cls, document: str) -> "Document":
        """Factory method to create a Document value object"""
        # Remove non-digits and normalize
        clean_document = re.sub(r"\D", "", document) if document else ""
        return cls(clean_document)

    @property
    def is_empty(self) -> bool:
        """Check if the document is empty (for anonymous customers)"""
        return not self.value or self.value.strip() == ""

    @property
    def formatted(self) -> str:
        """Return formatted CPF (XXX.XXX.XXX-XX)"""
        if not self.value or len(self.value) != 11:
            return self.value

        return f"{self.value[:3]}.{self.value[3:6]}.{self.value[6:9]}-{self.value[9:]}"
