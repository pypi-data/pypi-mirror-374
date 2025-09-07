import pytest

from digitalmeve.utils import format_identity


def test_format_identity_valid():
    """format_identity doit retourner la valeur de la clé 'identity'."""
    data = {"identity": "ABC123"}
    assert format_identity(data) == "ABC123"


def test_format_identity_invalid():
    """format_identity(None) doit lever AttributeError."""
    with pytest.raises(AttributeError):
        format_identity(None)
