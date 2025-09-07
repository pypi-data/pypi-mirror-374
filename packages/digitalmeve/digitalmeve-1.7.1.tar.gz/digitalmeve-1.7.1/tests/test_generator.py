from __future__ import annotations

from pathlib import Path

from digitalmeve.generator import generate_meve


def test_generate_meve_returns_dict(tmp_path: Path):
    # Create a temporary file
    file_path = tmp_path / "dummy.txt"
    file_path.write_text("hello meve")

    result = generate_meve(file_path)

    assert isinstance(result, dict)
    assert "issuer" in result
    assert "meve_version" in result
    assert "hash" in result
    assert "preview_b64" in result
